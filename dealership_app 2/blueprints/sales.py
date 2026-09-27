# blueprints/sales.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import get_db_connection, login_required, division_required
import mysql.connector

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/sales')
@login_required
def list_sales():
    dept   = request.args.get('dept', '').strip()
    search = request.args.get('q', '').strip()

    filters, params = [], []
    if dept:
        filters.append("ea.DepartmentID = %s"); params.append(dept)
    if search:
        filters.append("(c.Name LIKE %s OR v.Make LIKE %s OR v.Model LIKE %s)")
        params += [f'%{search}%', f'%{search}%', f'%{search}%']

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT s.*, c.Name AS CustomerName,
                   v.Make, v.Model, v.Year,
                   ea.Username AS SalesPerson,
                   d.Name AS DeptName
            FROM   SaleManagement s
            JOIN   Customer c         ON s.CustID     = c.CustID
            JOIN   VehicleManagement v ON s.VehicleID  = v.VehicleID
            JOIN   EmployeeAccount ea  ON s.EmployeeID = ea.EmployeeID
            JOIN   Department d        ON ea.DepartmentID = d.DepartmentID
            {where}
            ORDER  BY s.DateOfSale DESC
        """, params)
        sales = cursor.fetchall()

        cursor.execute("""
            SELECT DepartmentID, Name FROM Department
            WHERE DivisionID = 1
        """)
        departments = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        sales = []; departments = []
    finally:
        cursor.close(); conn.close()

    return render_template('sales/list.html', sales=sales,
                           departments=departments, dept=dept, search=search)


@sales_bp.route('/sales/new', methods=['GET', 'POST'])
@login_required
def new_sale():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT VehicleID, Make, Model, Year, Price
            FROM   VehicleManagement
            WHERE  AvailabilityStatus = 'available'
            ORDER  BY Make, Model
        """)
        vehicles = cursor.fetchall()
        cursor.execute("SELECT CustID, Name FROM Customer ORDER BY Name")
        customers = cursor.fetchall()
        cursor.execute("""
            SELECT EmployeeID, Username, Job FROM EmployeeAccount
            WHERE DepartmentID IN (SELECT DepartmentID FROM Department WHERE DivisionID=1)
        """)
        employees = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        vehicles = customers = employees = []
    finally:
        cursor.close(); conn.close()

    if request.method == 'POST':
        vehicle_id  = request.form['vehicle_id']
        cust_id     = request.form['cust_id']
        employee_id = request.form['employee_id']
        sale_price  = request.form['sale_price']
        date_of_sale= request.form['date_of_sale']
        payment     = request.form['payment_method']
        financing   = request.form.get('financing_option', 'N/A').strip() or 'N/A'

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO SaleManagement
                    (EmployeeID, VehicleID, CustID, SalePrice, DateOfSale, PaymentMethod, FinancingOption)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (employee_id, vehicle_id, cust_id, sale_price, date_of_sale, payment, financing))
            sale_id = cursor.lastrowid

            # Auto-update vehicle availability
            cursor.execute("""
                UPDATE VehicleManagement SET AvailabilityStatus='sold'
                WHERE VehicleID=%s
            """, (vehicle_id,))

            # Record financial transaction
            cursor.execute("""
                INSERT INTO FinancialTransactions
                    (Amount, Date, SaleID, ServiceID, PaymentID, TransactionType)
                VALUES (%s,%s,%s,NULL,NULL,'Vehicle Sale')
            """, (sale_price, date_of_sale, sale_id))

            conn.commit()
            flash("Sale recorded successfully.", "success")
            return redirect(url_for('sales.list_sales'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('sales/form.html',
                           vehicles=vehicles, customers=customers, employees=employees)
