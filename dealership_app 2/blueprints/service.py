# blueprints/service.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_connection, login_required
import mysql.connector

service_bp = Blueprint('service', __name__)


@service_bp.route('/service')
@login_required
def list_services():
    search = request.args.get('q', '').strip()
    filters, params = [], []
    if search:
        filters.append("(c.Name LIKE %s OR v.Make LIKE %s OR v.VIN LIKE %s)")
        params += [f'%{search}%', f'%{search}%', f'%{search}%']

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT sr.*,
                   c.Name AS CustomerName,
                   v.Make, v.Model, v.Year, v.VIN,
                   GROUP_CONCAT(p.Name ORDER BY p.PartID SEPARATOR ', ') AS Parts
            FROM   ServiceRecord sr
            JOIN   Customer c          ON sr.CustID    = c.CustID
            JOIN   VehicleManagement v ON sr.VehicleID = v.VehicleID
            LEFT   JOIN PartServices ps ON sr.ServiceID = ps.ServiceID
            LEFT   JOIN Part p          ON ps.PartID    = p.PartID
            {where}
            GROUP  BY sr.ServiceID
            ORDER  BY sr.ServiceDate DESC
        """, params)
        services = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        services = []
    finally:
        cursor.close(); conn.close()

    return render_template('service/list.html', services=services, search=search)


@service_bp.route('/service/<int:service_id>')
@login_required
def view_service(service_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sr.*, c.Name AS CustomerName,
                   v.Make, v.Model, v.Year, v.VIN
            FROM   ServiceRecord sr
            JOIN   Customer c          ON sr.CustID    = c.CustID
            JOIN   VehicleManagement v ON sr.VehicleID = v.VehicleID
            WHERE  sr.ServiceID = %s
        """, (service_id,))
        record = cursor.fetchone()

        cursor.execute("""
            SELECT p.Name, p.PartCost, ps.Quantity,
                   (p.PartCost * ps.Quantity) AS LineTotal
            FROM   PartServices ps
            JOIN   Part p ON ps.PartID = p.PartID
            WHERE  ps.ServiceID = %s
        """, (service_id,))
        parts = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        record = None; parts = []
    finally:
        cursor.close(); conn.close()

    if not record:
        flash("Service record not found.", "error")
        return redirect(url_for('service.list_services'))

    return render_template('service/view.html', record=record, parts=parts)


@service_bp.route('/service/new', methods=['GET', 'POST'])
@login_required
def new_service():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CustID, Name FROM Customer ORDER BY Name")
        customers = cursor.fetchall()
        cursor.execute("SELECT VehicleID, Make, Model, Year, VIN FROM VehicleManagement ORDER BY Make")
        vehicles = cursor.fetchall()
        cursor.execute("SELECT PartID, Name, PartCost FROM Part ORDER BY Name")
        parts = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        customers = vehicles = parts = []
    finally:
        cursor.close(); conn.close()

    if request.method == 'POST':
        cust_id      = request.form['cust_id']
        vehicle_id   = request.form['vehicle_id']
        service_date = request.form['service_date']
        service_price= request.form['service_price']
        part_ids     = request.form.getlist('part_id')
        quantities   = request.form.getlist('quantity')

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ServiceRecord (ServiceDate, ServicePrice, CustID, VehicleID)
                VALUES (%s,%s,%s,%s)
            """, (service_date, service_price, cust_id, vehicle_id))
            service_id = cursor.lastrowid

            for pid, qty in zip(part_ids, quantities):
                if pid and int(qty) > 0:
                    cursor.execute("""
                        INSERT INTO PartServices (ServiceID, PartID, Quantity)
                        VALUES (%s,%s,%s)
                    """, (service_id, pid, qty))

            # Record financial transaction
            cursor.execute("""
                INSERT INTO FinancialTransactions
                    (Amount, Date, SaleID, ServiceID, PaymentID, TransactionType)
                VALUES (%s,%s,NULL,%s,NULL,'Service')
            """, (service_price, service_date, service_id))

            conn.commit()
            flash("Service record created.", "success")
            return redirect(url_for('service.view_service', service_id=service_id))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('service/form.html',
                           customers=customers, vehicles=vehicles, parts=parts)


@service_bp.route('/service/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ServiceRecord WHERE ServiceID = %s", (service_id,))
        record = cursor.fetchone()
        cursor.execute("SELECT CustID, Name FROM Customer ORDER BY Name")
        customers = cursor.fetchall()
        cursor.execute("SELECT VehicleID, Make, Model, Year FROM VehicleManagement ORDER BY Make")
        vehicles = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('service.list_services'))
    finally:
        cursor.close(); conn.close()

    if not record:
        flash("Service record not found.", "error")
        return redirect(url_for('service.list_services'))

    if request.method == 'POST':
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ServiceRecord
                SET ServiceDate=%s, ServicePrice=%s, CustID=%s, VehicleID=%s
                WHERE ServiceID=%s
            """, (
                request.form['service_date'],
                request.form['service_price'],
                request.form['cust_id'],
                request.form['vehicle_id'],
                service_id
            ))
            conn.commit()
            flash("Service record updated.", "success")
            return redirect(url_for('service.view_service', service_id=service_id))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('service/edit.html',
                           record=record, customers=customers, vehicles=vehicles)
