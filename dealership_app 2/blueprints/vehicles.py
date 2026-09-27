# blueprints/vehicles.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_connection, login_required
import mysql.connector

vehicles_bp = Blueprint('vehicles', __name__)


@vehicles_bp.route('/vehicles')
@login_required
def list_vehicles():
    make  = request.args.get('make', '').strip()
    model = request.args.get('model', '').strip()
    year  = request.args.get('year', '').strip()
    max_price = request.args.get('max_price', '').strip()
    condition = request.args.get('condition', '').strip()

    filters, params = [], []
    if make:
        filters.append("Make LIKE %s"); params.append(f'%{make}%')
    if model:
        filters.append("Model LIKE %s"); params.append(f'%{model}%')
    if year:
        filters.append("Year = %s"); params.append(year)
    if max_price:
        filters.append("Price <= %s"); params.append(max_price)
    if condition:
        filters.append("VehicleCondition = %s"); params.append(condition)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT * FROM VehicleManagement {where}
            ORDER BY Make, Model, Year
        """, params)
        vehicles = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        vehicles = []
    finally:
        cursor.close(); conn.close()

    return render_template('vehicles/list.html', vehicles=vehicles,
                           make=make, model=model, year=year,
                           max_price=max_price, condition=condition)


@vehicles_bp.route('/vehicles/<int:vehicle_id>')
@login_required
def view_vehicle(vehicle_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM VehicleManagement WHERE VehicleID = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
        cursor.execute("""
            SELECT sr.*, c.Name AS CustomerName
            FROM   ServiceRecord sr
            JOIN   Customer c ON sr.CustID = c.CustID
            WHERE  sr.VehicleID = %s
            ORDER  BY sr.ServiceDate DESC
        """, (vehicle_id,))
        service_history = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        vehicle = None; service_history = []
    finally:
        cursor.close(); conn.close()

    if not vehicle:
        flash("Vehicle not found.", "error")
        return redirect(url_for('vehicles.list_vehicles'))

    return render_template('vehicles/view.html', vehicle=vehicle,
                           service_history=service_history)


@vehicles_bp.route('/vehicles/new', methods=['GET', 'POST'])
@login_required
def new_vehicle():
    if request.method == 'POST':
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO VehicleManagement
                    (VIN, Make, Model, Year, Price, Mileage, VehicleCondition, AvailabilityStatus)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                request.form['vin'].strip(),
                request.form['make'].strip(),
                request.form['model'].strip(),
                request.form['year'],
                request.form['price'],
                request.form['mileage'],
                request.form['condition'],
                request.form['status']
            ))
            conn.commit()
            flash("Vehicle added to inventory.", "success")
            return redirect(url_for('vehicles.list_vehicles'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('vehicles/form.html', vehicle=None)


@vehicles_bp.route('/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM VehicleManagement WHERE VehicleID = %s", (vehicle_id,))
        vehicle = cursor.fetchone()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('vehicles.list_vehicles'))
    finally:
        cursor.close(); conn.close()

    if not vehicle:
        flash("Vehicle not found.", "error")
        return redirect(url_for('vehicles.list_vehicles'))

    if request.method == 'POST':
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE VehicleManagement
                SET VIN=%s, Make=%s, Model=%s, Year=%s, Price=%s,
                    Mileage=%s, VehicleCondition=%s, AvailabilityStatus=%s
                WHERE VehicleID=%s
            """, (
                request.form['vin'].strip(),
                request.form['make'].strip(),
                request.form['model'].strip(),
                request.form['year'],
                request.form['price'],
                request.form['mileage'],
                request.form['condition'],
                request.form['status'],
                vehicle_id
            ))
            conn.commit()
            flash("Vehicle updated.", "success")
            return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle_id))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('vehicles/form.html', vehicle=vehicle)
