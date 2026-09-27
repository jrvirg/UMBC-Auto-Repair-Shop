# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection
import mysql.connector

auth_bp = Blueprint('auth', __name__)


# ------------------------------------------------------------------
# Login  (GET / POST  →  /)
# ------------------------------------------------------------------
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'employee_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    if 'customer_id' in session:
        return redirect(url_for('auth.customer_portal'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Try Administrator table first
            cursor.execute(
                "SELECT * FROM Administrator WHERE Username = %s", (username,)
            )
            admin = cursor.fetchone()

            if admin and check_password_hash(admin['Password'], password):
                session['employee_id']  = admin['AdminID']
                session['username']     = admin['Username']
                session['job']          = 'Administrator'
                session['department_id'] = None
                session['division_id']  = None
                cursor.close(); conn.close()
                return redirect(url_for('dashboard.dashboard'))

            # Then try EmployeeAccount
            cursor.execute("""
                SELECT ea.*, d.DivisionID
                FROM   EmployeeAccount ea
                JOIN   Department d ON ea.DepartmentID = d.DepartmentID
                WHERE  ea.Username = %s
            """, (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['Password'], password):
                session['employee_id']   = user['EmployeeID']
                session['username']      = user['Username']
                session['job']           = user['Job']
                session['department_id'] = user['DepartmentID']
                session['division_id']   = user['DivisionID']
                cursor.close(); conn.close()
                return redirect(url_for('dashboard.dashboard'))

            # Then try CustomerAccount
            cursor.execute("""
                SELECT ca.*, c.Name AS CustomerName, c.CustID
                FROM   CustomerAccount ca
                JOIN   Customer c ON ca.CustID = c.CustID
                WHERE  ca.Username = %s
            """, (username,))
            cust_account = cursor.fetchone()
            cursor.close(); conn.close()

            if cust_account and check_password_hash(cust_account['Password'], password):
                session['customer_id']   = cust_account['CustID']
                session['customer_name'] = cust_account['CustomerName']
                session['customer_username'] = cust_account['Username']
                return redirect(url_for('auth.customer_portal'))

            flash("Invalid username or password.", "error")

        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")

    return render_template('login.html')


# ------------------------------------------------------------------
# Customer Sign-Up  (GET / POST  →  /signup)
# ------------------------------------------------------------------
@auth_bp.route('/signup', methods=['POST'])
def signup():
    name     = request.form.get('name', '').strip()
    email    = request.form.get('email', '').strip()
    phone    = request.form.get('phone', '').strip()
    street   = request.form.get('street', '').strip()
    city     = request.form.get('city', '').strip()
    state    = request.form.get('state', '').strip().upper()
    zip_code = request.form.get('zip', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm  = request.form.get('confirm_password', '')

    if password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for('auth.login'))

    if not all([name, email, street, city, state, zip_code, username, password]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for('auth.login'))

    address = f"{street}, {city}, {state} {zip_code}"
    hashed  = generate_password_hash(password)

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check username not taken
        cursor.execute("SELECT AccountID FROM CustomerAccount WHERE Username = %s", (username,))
        if cursor.fetchone():
            flash("That username is already taken. Please choose another.", "error")
            cursor.close(); conn.close()
            return redirect(url_for('auth.login'))

        # Check email not taken
        cursor.execute("SELECT CustID FROM Customer WHERE Email = %s", (email,))
        if cursor.fetchone():
            flash("An account with that email already exists.", "error")
            cursor.close(); conn.close()
            return redirect(url_for('auth.login'))

        # Insert Customer record
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customer (Name, Address, Email) VALUES (%s, %s, %s)",
            (name, address, email)
        )
        cust_id = cursor.lastrowid

        # Insert phone if provided
        if phone:
            cursor.execute(
                "INSERT INTO CustomerPhoneNumbers (CustID, PhoneNumber) VALUES (%s, %s)",
                (cust_id, phone)
            )

        # Insert CustomerAccount
        cursor.execute(
            "INSERT INTO CustomerAccount (CustID, Username, Password) VALUES (%s, %s, %s)",
            (cust_id, username, hashed)
        )
        conn.commit()

        # Log them in
        session['customer_id']       = cust_id
        session['customer_name']     = name
        session['customer_username'] = username

        flash(f"Welcome, {name}! Your account has been created.", "success")
        cursor.close(); conn.close()
        return redirect(url_for('auth.customer_portal'))

    except mysql.connector.IntegrityError as e:
        flash(f"Registration error: {e}", "error")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")

    return redirect(url_for('auth.login'))


# ------------------------------------------------------------------
# Customer Portal  (GET  →  /customer/portal)
# ------------------------------------------------------------------
@auth_bp.route('/customer/portal')
def customer_portal():
    if 'customer_id' not in session:
        flash("Please log in to view your portal.", "error")
        return redirect(url_for('auth.login'))

    cust_id = session['customer_id']
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Customer WHERE CustID = %s", (cust_id,))
        customer = cursor.fetchone()

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

        cursor.close(); conn.close()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        customer = phones = sales = services = []

    return render_template('customer_portal.html',
                           customer=customer, phones=phones,
                           sales=sales, services=services)


# ------------------------------------------------------------------
# Logout
# ------------------------------------------------------------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))

# ------------------------------------------------------------------
# Register Employee acount
# ------------------------------------------------------------------


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Handle the form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        job = request.form['job']
        department = request.form['department']
        
        # 1. Hash the password using a secure algorithm (pbkdf2:sha256 by default)
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 2. Insert the new user into the MySQL database
            cursor.execute(
                "INSERT INTO EmployeeAccount (username, password, DepartmentID ,Job) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, department, job)
            )
            # 3. Commit the transaction (required to save INSERT/UPDATE/DELETE changes)
            conn.commit()
            
            # Redirect the user to the login page after successful registration
            flash("You have been successfully registered.", "success")
            return redirect(url_for('auth.login'))
            
        except mysql.connector.IntegrityError:
            # This catches the error if the username already exists due to the UNIQUE constraint
            return "That username is already taken. Please choose another."
            
        finally:
            # Always close your connections, even if an error occurs
            cursor.close()
            conn.close()

    # If it's a GET request (just visiting the page), show the registration form
    return render_template('register.html')