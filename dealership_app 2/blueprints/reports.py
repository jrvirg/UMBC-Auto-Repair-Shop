# blueprints/reports.py
from flask import Blueprint, render_template, request, flash
from utils import get_db_connection, login_required
import mysql.connector

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    return render_template('reports/index.html')


@reports_bp.route('/reports/sales')
@login_required
def sales_report():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')

    filters, params = [], []
    if date_from:
        filters.append("s.DateOfSale >= %s"); params.append(date_from)
    if date_to:
        filters.append("s.DateOfSale <= %s"); params.append(date_to)
    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"""
            SELECT COUNT(*) AS TotalSold, SUM(SalePrice) AS TotalRevenue
            FROM   SaleManagement s {where}
        """, params)
        summary = cursor.fetchone()

        cursor.execute(f"""
            SELECT d.Name AS Department, COUNT(*) AS Sales, SUM(s.SalePrice) AS Revenue
            FROM   SaleManagement s
            JOIN   EmployeeAccount ea ON s.EmployeeID = ea.EmployeeID
            JOIN   Department d       ON ea.DepartmentID = d.DepartmentID
            {where}
            GROUP  BY d.DepartmentID, d.Name
            ORDER  BY Revenue DESC
        """, params)
        by_dept = cursor.fetchall()

        cursor.execute(f"""
            SELECT DATE_FORMAT(s.DateOfSale,'%Y-%m') AS Month,
                   COUNT(*) AS Sales, SUM(s.SalePrice) AS Revenue
            FROM   SaleManagement s {where}
            GROUP  BY Month ORDER BY Month
        """, params)
        by_month = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        summary = by_dept = by_month = []
    finally:
        cursor.close(); conn.close()

    return render_template('reports/sales.html',
                           summary=summary, by_dept=by_dept, by_month=by_month,
                           date_from=date_from, date_to=date_to)


@reports_bp.route('/reports/service')
@login_required
def service_report():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS TotalServices, SUM(ServicePrice) AS TotalRevenue
            FROM   ServiceRecord
        """)
        summary = cursor.fetchone()

        cursor.execute("""
            SELECT p.Name AS Part, SUM(ps.Quantity) AS UsedCount
            FROM   PartServices ps JOIN Part p ON ps.PartID = p.PartID
            GROUP  BY p.PartID, p.Name
            ORDER  BY UsedCount DESC
            LIMIT 10
        """)
        top_parts = cursor.fetchall()

        cursor.execute("""
            SELECT DATE_FORMAT(ServiceDate,'%Y-%m') AS Month,
                   COUNT(*) AS Services, SUM(ServicePrice) AS Revenue
            FROM   ServiceRecord
            GROUP  BY Month ORDER BY Month
        """)
        by_month = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        summary = top_parts = by_month = []
    finally:
        cursor.close(); conn.close()

    return render_template('reports/service.html',
                           summary=summary, top_parts=top_parts, by_month=by_month)


@reports_bp.route('/reports/loans')
@login_required
def loan_report():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT LoanApprovalStatus AS Status, COUNT(*) AS Count,
                   SUM(LoanAmount) AS TotalAmount
            FROM   FinancialServicesAndLoanManagement
            GROUP  BY LoanApprovalStatus
        """)
        by_status = cursor.fetchall()

        cursor.execute("""
            SELECT l.LoanID, c.Name AS Customer, l.LoanAmount,
                   l.MonthlyPayment, l.LoanApprovalStatus,
                   COALESCE(SUM(p.OwedAmount),0) AS TotalPaid,
                   (l.LoanAmount - COALESCE(SUM(p.OwedAmount),0)) AS Balance
            FROM   FinancialServicesAndLoanManagement l
            JOIN   Customer c ON l.CustID = c.CustID
            LEFT   JOIN LoanServicePayments p ON l.LoanID = p.LoanID
            GROUP  BY l.LoanID, c.Name, l.LoanAmount, l.MonthlyPayment, l.LoanApprovalStatus
            ORDER  BY Balance DESC
        """)
        loans = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        by_status = loans = []
    finally:
        cursor.close(); conn.close()

    return render_template('reports/loans.html', by_status=by_status, loans=loans)


@reports_bp.route('/reports/accounting')
@login_required
def accounting_report():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT SUM(Amount) AS TotalRevenue,
                   COUNT(*)    AS TotalTransactions
            FROM   FinancialTransactions
        """)
        summary = cursor.fetchone()

        cursor.execute("""
            SELECT TransactionType, SUM(Amount) AS Total, COUNT(*) AS Count
            FROM   FinancialTransactions
            GROUP  BY TransactionType
        """)
        by_type = cursor.fetchall()

        cursor.execute("""
            SELECT d.Name AS Department,
                   COUNT(s.SaleID) AS Sales,
                   COALESCE(SUM(s.SalePrice),0) AS Revenue
            FROM   Department d
            LEFT   JOIN EmployeeAccount ea ON d.DepartmentID = ea.DepartmentID
            LEFT   JOIN SaleManagement s   ON ea.EmployeeID  = s.EmployeeID
            GROUP  BY d.DepartmentID, d.Name
            ORDER  BY Revenue DESC
        """)
        by_dept = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        summary = by_type = by_dept = []
    finally:
        cursor.close(); conn.close()

    return render_template('reports/accounting.html',
                           summary=summary, by_type=by_type, by_dept=by_dept)
