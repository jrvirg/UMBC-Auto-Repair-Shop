# utils.py
from functools import wraps
from flask import session, flash, redirect, url_for
import mysql.connector

# ------------------------------------------------------------------
# Role → department/division mapping
# These job titles exist in EmployeeAccount.Job
# ------------------------------------------------------------------
ROLE_SALES    = 'Sales Associate'
ROLE_MANAGER  = 'Sales Manager'
ROLE_MECHANIC = 'Mechanic'
ROLE_BODY     = 'Body Tech'
ROLE_LOAN     = 'Loan Officer'
ROLE_PARTS    = 'Parts Clerk'
ROLE_ADMIN    = 'Administrator'      # special – see note below

# Division IDs in the DB
DIV_SALES    = 1
DIV_SERVICE  = 2
DIV_FINANCE  = 3

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="my-secret-pw",
        database="GroupTwoDealership",
        port=3306
    )

# ------------------------------------------------------------------
# Decorators
# ------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*allowed_jobs):
    """Restrict a route to employees whose Job is in allowed_jobs."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'employee_id' not in session:
                flash("You need to be logged in.", "error")
                return redirect(url_for('auth.login'))
            if session.get('job') not in allowed_jobs:
                flash("You do not have permission to access that page.", "error")
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def division_required(*allowed_division_ids):
    """Restrict a route to employees in the given division(s)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'employee_id' not in session:
                flash("You need to be logged in.", "error")
                return redirect(url_for('auth.login'))
            if session.get('division_id') not in allowed_division_ids:
                flash("You do not have permission to access that page.", "error")
                return redirect(url_for('dashboard.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
