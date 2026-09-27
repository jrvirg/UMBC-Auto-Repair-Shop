# blueprints/loans.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_connection, login_required
import mysql.connector

loans_bp = Blueprint('loans', __name__)


@loans_bp.route('/loans')
@login_required
def list_loans():
    status = request.args.get('status', '').strip()
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        where  = "WHERE l.LoanApprovalStatus = %s" if status else ""
        params = [status] if status else []
        cursor.execute(f"""
            SELECT l.*, c.Name AS CustomerName,
                   v.Make, v.Model, v.Year
            FROM   FinancialServicesAndLoanManagement l
            JOIN   Customer c          ON l.CustID    = c.CustID
            JOIN   VehicleManagement v ON l.VehicleID = v.VehicleID
            {where}
            ORDER  BY l.LoanID DESC
        """, params)
        loans = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        loans = []
    finally:
        cursor.close(); conn.close()

    return render_template('loans/list.html', loans=loans, status=status)


@loans_bp.route('/loans/<int:loan_id>')
@login_required
def view_loan(loan_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.*, c.Name AS CustomerName,
                   v.Make, v.Model, v.Year
            FROM   FinancialServicesAndLoanManagement l
            JOIN   Customer c          ON l.CustID    = c.CustID
            JOIN   VehicleManagement v ON l.VehicleID = v.VehicleID
            WHERE  l.LoanID = %s
        """, (loan_id,))
        loan = cursor.fetchone()

        cursor.execute("""
            SELECT * FROM LoanServicePayments
            WHERE LoanID = %s ORDER BY DueDate
        """, (loan_id,))
        payments = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        loan = None; payments = []
    finally:
        cursor.close(); conn.close()

    if not loan:
        flash("Loan not found.", "error")
        return redirect(url_for('loans.list_loans'))

    return render_template('loans/view.html', loan=loan, payments=payments)


@loans_bp.route('/loans/new', methods=['GET', 'POST'])
@login_required
def new_loan():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CustID, Name FROM Customer ORDER BY Name")
        customers = cursor.fetchall()
        cursor.execute("""
            SELECT VehicleID, Make, Model, Year, Price
            FROM   VehicleManagement WHERE AvailabilityStatus != 'sold'
            ORDER BY Make
        """)
        vehicles = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        customers = vehicles = []
    finally:
        cursor.close(); conn.close()

    if request.method == 'POST':
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO FinancialServicesAndLoanManagement
                    (CustID, VehicleID, LoanAmount, InterestRate, LoanTerm,
                     MonthlyPayment, LoanApprovalStatus)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                request.form['cust_id'],
                request.form['vehicle_id'],
                request.form['loan_amount'],
                request.form['interest_rate'],
                request.form['loan_term'],
                request.form['monthly_payment'],
                request.form['approval_status']
            ))
            conn.commit()
            flash("Loan record created.", "success")
            return redirect(url_for('loans.list_loans'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('loans/form.html', customers=customers, vehicles=vehicles)


@loans_bp.route('/loans/<int:loan_id>/payment', methods=['GET', 'POST'])
@login_required
def add_payment(loan_id):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.*, c.Name AS CustomerName
            FROM   FinancialServicesAndLoanManagement l
            JOIN   Customer c ON l.CustID = c.CustID
            WHERE  l.LoanID = %s
        """, (loan_id,))
        loan = cursor.fetchone()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('loans.list_loans'))
    finally:
        cursor.close(); conn.close()

    if not loan:
        flash("Loan not found.", "error")
        return redirect(url_for('loans.list_loans'))

    if request.method == 'POST':
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO LoanServicePayments
                    (LoanID, Name, DueDate, OwedAmount, NextDueAmount)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                loan_id,
                loan['CustomerName'],
                request.form['due_date'],
                request.form['owed_amount'],
                request.form['next_due_amount']
            ))
            payment_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO FinancialTransactions
                    (Amount, Date, SaleID, ServiceID, PaymentID, TransactionType)
                VALUES (%s,%s,NULL,NULL,%s,'Loan Payment')
            """, (request.form['owed_amount'], request.form['due_date'], payment_id))

            conn.commit()
            flash("Payment recorded.", "success")
            return redirect(url_for('loans.view_loan', loan_id=loan_id))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close(); conn.close()

    return render_template('loans/payment.html', loan=loan)
