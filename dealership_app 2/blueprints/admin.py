# blueprints/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from utils import get_db_connection, login_required, roles_required
import mysql.connector

admin_bp = Blueprint('admin', __name__)


def admin_only(f):
    """Shorthand: only Administrators may access these routes."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('job') != 'Administrator':
            flash("Administrator access required.", "error")
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return wrapper


# ------------------------------------------------------------------
# Employee account management
# ------------------------------------------------------------------
@admin_bp.route('/admin/employees')
@login_required
@admin_only
def list_employees():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ea.*, d.Name AS DeptName, div.Name AS DivName
            FROM   EmployeeAccount ea
            JOIN   Department d  ON ea.DepartmentID = d.DepartmentID
            JOIN   Division div  ON d.DivisionID    = div.DivisionID
            ORDER  BY ea.Username
        """)
        employees = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        employees = []
    finally:
        cursor.close(); conn.close()

    return render_template('admin/employees.html', employees=employees)


@admin_bp.route('/admin/employees/new', methods=['GET', 'POST'])
@login_required
@admin_only
def new_employee():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DepartmentID, Name FROM Department ORDER BY Name")
        departments = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        departments = []
    finally:
        cursor.close(); conn.close()

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = generate_password_hash(request.form['password'])
        job      = request.form['job'].strip()
        dept_id  = request.form['department_id']

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO EmployeeAccount (DepartmentID, Username, Password, Job)
                VALUES (%s,%s,%s,%s)
            """, (dept_id, username, password, job))
            conn.commit()
            flash(f"Employee '{username}' created.", "success")
            return redirect(url_for('admin.list_employees'))
        except mysql.connector.IntegrityError:
            flash("Username already exists.", "error")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('admin/employee_form.html', employee=None, departments=departments)


@admin_bp.route('/admin/employees/<int:emp_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_employee(emp_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM EmployeeAccount WHERE EmployeeID = %s", (emp_id,))
        employee = cursor.fetchone()
        cursor.execute("SELECT DepartmentID, Name FROM Department ORDER BY Name")
        departments = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('admin.list_employees'))
    finally:
        cursor.close(); conn.close()

    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for('admin.list_employees'))

    if request.method == 'POST':
        job     = request.form['job'].strip()
        dept_id = request.form['department_id']
        new_pw  = request.form.get('password', '').strip()

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            if new_pw:
                cursor.execute("""
                    UPDATE EmployeeAccount SET Job=%s, DepartmentID=%s, Password=%s
                    WHERE EmployeeID=%s
                """, (job, dept_id, generate_password_hash(new_pw), emp_id))
            else:
                cursor.execute("""
                    UPDATE EmployeeAccount SET Job=%s, DepartmentID=%s
                    WHERE EmployeeID=%s
                """, (job, dept_id, emp_id))
            conn.commit()
            flash("Employee updated.", "success")
            return redirect(url_for('admin.list_employees'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('admin/employee_form.html',
                           employee=employee, departments=departments)


# ------------------------------------------------------------------
# Division / Department management
# ------------------------------------------------------------------
@admin_bp.route('/admin/divisions')
@login_required
@admin_only
def list_divisions():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT div.*, COUNT(d.DepartmentID) AS DeptCount
            FROM Division div
            LEFT JOIN Department d ON div.DivisionID = d.DivisionID
            GROUP BY div.DivisionID
            ORDER BY div.Name
        """)
        divisions = cursor.fetchall()
        cursor.execute("""
            SELECT d.*, div.Name AS DivName
            FROM Department d JOIN Division div ON d.DivisionID = div.DivisionID
            ORDER BY div.Name, d.Name
        """)
        departments = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        divisions = departments = []
    finally:
        cursor.close(); conn.close()

    return render_template('admin/divisions.html',
                           divisions=divisions, departments=departments)


@admin_bp.route('/admin/divisions/add', methods=['POST'])
@login_required
@admin_only
def add_division():
    name = request.form.get('name', '').strip()
    if name:
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Division (Name) VALUES (%s)", (name,))
            conn.commit()
            flash(f"Division '{name}' added.", "success")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()
    return redirect(url_for('admin.list_divisions'))


@admin_bp.route('/admin/departments/add', methods=['POST'])
@login_required
@admin_only
def add_department():
    name   = request.form.get('name', '').strip()
    div_id = request.form.get('division_id')
    if name and div_id:
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Department (DivisionID, Name) VALUES (%s,%s)",
                           (div_id, name))
            conn.commit()
            flash(f"Department '{name}' added.", "success")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()
    return redirect(url_for('admin.list_divisions'))
