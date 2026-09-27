# blueprints/accounting.py
from flask import Blueprint, render_template, request, flash
from utils import get_db_connection, login_required
import mysql.connector

accounting_bp = Blueprint('accounting', __name__)


@accounting_bp.route('/accounting')
@login_required
def overview():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total revenue by transaction type
        cursor.execute("""
            SELECT TransactionType,
                   COUNT(*)     AS Count,
                   SUM(Amount)  AS Total
            FROM   FinancialTransactions
            GROUP  BY TransactionType
            ORDER  BY Total DESC
        """)
        by_type = cursor.fetchall()

        # Monthly revenue summary
        cursor.execute("""
            SELECT DATE_FORMAT(Date,'%Y-%m') AS Month,
                   SUM(Amount) AS Total,
                   COUNT(*)    AS Transactions
            FROM   FinancialTransactions
            GROUP  BY Month
            ORDER  BY Month DESC
            LIMIT 12
        """)
        monthly = cursor.fetchall()

        # Recent transactions
        cursor.execute("""
            SELECT ft.*,
                   COALESCE(c1.Name, c2.Name, c3.Name) AS RelatedCustomer
            FROM   FinancialTransactions ft
            LEFT   JOIN SaleManagement sm     ON ft.SaleID    = sm.SaleID
            LEFT   JOIN ServiceRecord sr       ON ft.ServiceID = sr.ServiceID
            LEFT   JOIN LoanServicePayments lp ON ft.PaymentID = lp.PaymentID
            LEFT   JOIN Customer c1 ON sm.CustID = c1.CustID
            LEFT   JOIN Customer c2 ON sr.CustID = c2.CustID
            LEFT   JOIN FinancialServicesAndLoanManagement fl ON lp.LoanID = fl.LoanID
            LEFT   JOIN Customer c3 ON fl.CustID = c3.CustID
            ORDER  BY ft.Date DESC, ft.TransactionID DESC
            LIMIT 50
        """)
        transactions = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        by_type = monthly = transactions = []
    finally:
        cursor.close(); conn.close()

    return render_template('accounting/overview.html',
                           by_type=by_type, monthly=monthly,
                           transactions=transactions)
