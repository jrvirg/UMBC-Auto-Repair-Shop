# blueprints/customers.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import get_db_connection, login_required
import mysql.connector

customers_bp = Blueprint('customers', __name__)


def _parse_address(address):
    """Split 'Street, City, STATE ZIP' back into parts for the edit form."""
    parts = [p.strip() for p in address.split(',')]
    if len(parts) >= 3:
        street = parts[0]
        city   = parts[1]
        sv     = parts[2].strip().split(' ', 1)
        state  = sv[0] if sv else ''
        zip_c  = sv[1] if len(sv) > 1 else ''
    elif len(parts) == 2:
        street, city = parts[0], parts[1]
        state = zip_c = ''
    else:
        street = address
        city = state = zip_c = ''
    return street, city, state, zip_c


@customers_bp.route('/customers')
@login_required
def list_customers():
    search = request.args.get('q', '').strip()
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if search:
            cursor.execute("""
                SELECT c.*,
                       GROUP_CONCAT(p.PhoneNumber ORDER BY p.PhoneID SEPARATOR ', ') AS Phones
                FROM   Customer c
                LEFT   JOIN CustomerPhoneNumbers p ON c.CustID = p.CustID
                WHERE  c.Name LIKE %s OR c.Email LIKE %s
                GROUP  BY c.CustID
                ORDER  BY c.Name
            """, (f'%{search}%', f'%{search}%'))
        else:
            cursor.execute("""
                SELECT c.*,
                       GROUP_CONCAT(p.PhoneNumber ORDER BY p.PhoneID SEPARATOR ', ') AS Phones
                FROM   Customer c
                LEFT   JOIN CustomerPhoneNumbers p ON c.CustID = p.CustID
                GROUP  BY c.CustID
                ORDER  BY c.Name
            """)
        customers = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        customers = []
    finally:
        cursor.close(); conn.close()

    return render_template('customers/list.html', customers=customers, search=search)


@customers_bp.route('/customers/<int:cust_id>')
@login_required
def view_customer(cust_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Customer WHERE CustID = %s", (cust_id,))
        customer = cursor.fetchone()
        if not customer:
            flash("Customer not found.", "error")
            return redirect(url_for('customers.list_customers'))

        cursor.execute("SELECT * FROM CustomerPhoneNumbers WHERE CustID = %s", (cust_id,))
        phones = cursor.fetchall()

        cursor.execute("""
            SELECT s.*, v.Make, v.Model, v.Year
            FROM   SaleManagement s
            JOIN   VehicleManagement v ON s.VehicleID = v.VehicleID
            WHERE  s.CustID = %s
            ORDER  BY s.DateOfSale DESC
        """, (cust_id,))
        sales = cursor.fetchall()

        cursor.execute("""
            SELECT sr.*, v.Make, v.Model, v.Year
            FROM   ServiceRecord sr
            JOIN   VehicleManagement v ON sr.VehicleID = v.VehicleID
            WHERE  sr.CustID = %s
            ORDER  BY sr.ServiceDate DESC
        """, (cust_id,))
        services = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        customer = phones = sales = services = []
    finally:
        cursor.close(); conn.close()

    return render_template('customers/view.html',
                           customer=customer, phones=phones,
                           sales=sales, services=services)


@customers_bp.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip()
        street   = request.form.get('street', '').strip()
        city     = request.form.get('city', '').strip()
        state    = request.form.get('state', '').strip().upper()
        zip_code = request.form.get('zip', '').strip()
        address  = f"{street}, {city}, {state} {zip_code}"
        phones   = [p.strip() for p in request.form.get('phones', '').split(',') if p.strip()]

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Customer (Name, Address, Email)
                VALUES (%s, %s, %s)
            """, (name, address, email))
            cust_id = cursor.lastrowid

            for phone in phones:
                cursor.execute("""
                    INSERT INTO CustomerPhoneNumbers (CustID, PhoneNumber)
                    VALUES (%s, %s)
                """, (cust_id, phone))

            conn.commit()
            flash("Customer registered successfully.", "success")
            return redirect(url_for('customers.view_customer', cust_id=cust_id))

        except mysql.connector.IntegrityError as e:
            flash(f"Error: {e}", "error")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('customers/form.html', customer=None,
                           addr_street='', addr_city='', addr_state='', addr_zip='')


@customers_bp.route('/customers/<int:cust_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(cust_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer WHERE CustID = %s", (cust_id,))
        customer = cursor.fetchone()
        cursor.execute("SELECT PhoneNumber FROM CustomerPhoneNumbers WHERE CustID = %s", (cust_id,))
        phones = [r['PhoneNumber'] for r in cursor.fetchall()]
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('customers.list_customers'))
    finally:
        cursor.close(); conn.close()

    if not customer:
        flash("Customer not found.", "error")
        return redirect(url_for('customers.list_customers'))

    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip()
        street   = request.form.get('street', '').strip()
        city     = request.form.get('city', '').strip()
        state    = request.form.get('state', '').strip().upper()
        zip_code = request.form.get('zip', '').strip()
        address  = f"{street}, {city}, {state} {zip_code}"
        new_phones = [p.strip() for p in request.form.get('phones', '').split(',') if p.strip()]

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Customer SET Name=%s, Address=%s, Email=%s WHERE CustID=%s
            """, (name, address, email, cust_id))
            cursor.execute("DELETE FROM CustomerPhoneNumbers WHERE CustID = %s", (cust_id,))
            for phone in new_phones:
                cursor.execute("""
                    INSERT INTO CustomerPhoneNumbers (CustID, PhoneNumber) VALUES (%s, %s)
                """, (cust_id, phone))
            conn.commit()
            flash("Customer updated.", "success")
            return redirect(url_for('customers.view_customer', cust_id=cust_id))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    street, city, state, zip_c = _parse_address(customer.get('Address', ''))
    return render_template('customers/form.html', customer=customer,
                           phones_str=', '.join(phones),
                           addr_street=street, addr_city=city,
                           addr_state=state, addr_zip=zip_c)
