======================================================
  Group 2 Dealership App — Setup & Run Guide
  CMSC 461 SP26 — Matthew, Jackson, Stephen, Ohm
======================================================

PROJECT STRUCTURE
-----------------
dealership/
├── app.py                  # Entry point — registers all blueprints
├── utils.py                # DB connection + login/role decorators
├── setup_accounts.py       # ONE-TIME: hashes all DB passwords
├── patch.sql               # ONE-TIME: adds Administrator table + AUTO_INCREMENT
│
├── blueprints/
│   ├── auth.py             # Login / logout
│   ├── dashboard.py        # Role-aware dashboard
│   ├── customers.py        # Customer CRUD + search
│   ├── vehicles.py         # Vehicle inventory CRUD + filter
│   ├── sales.py            # Sales transactions
│   ├── service.py          # Maintenance service records + parts
│   ├── loans.py            # Loan management + payment history
│   ├── accounting.py       # Financial transaction overview
│   ├── reports.py          # Sales / Service / Loan / Accounting reports
│   └── admin.py            # User accounts + divisions + departments
│
└── templates/
    ├── layout.html, login.html, dashboard.html
    ├── customers/  list, view, form
    ├── vehicles/   list, view, form
    ├── sales/      list, form
    ├── service/    list, view, form, edit
    ├── loans/      list, view, form, payment
    ├── accounting/ overview
    ├── reports/    index, sales, service, loans, accounting
    └── admin/      employees, employee_form, divisions


PREREQUISITES
-------------
- Python 3.x in PATH  (miniconda recommended)
- MySQL running in Docker on port 3306:
    docker run --name mysql-dealership -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 -d mysql:8

- Install Python packages:
    pip install Flask mysql-connector-python werkzeug


DATABASE SETUP (run in order)
------------------------------
1. Import the schema:
       mysql -u root -pmy-secret-pw < createDDL.sql

2. Load sample data:
       mysql -u root -pmy-secret-pw < loadAll.sql

3. Apply patch (Administrator table + AUTO_INCREMENT):
       mysql -u root -pmy-secret-pw GroupTwoDealership < patch.sql

4. Hash all employee passwords:
       python setup_accounts.py


RUN THE APP
-----------
    python app.py

Access at:  http://localhost:8000   or   http://127.0.0.1:8000


LOGIN ACCOUNTS
--------------
Username    Password     Role                Division
--------    --------     ----                --------
admin       admin123     Administrator       All access
msmith      password1    Sales Associate     Sales
jdoe        password2    Sales Associate     Sales
kwhite      password3    Sales Manager       Sales
lgreen      password4    Mechanic            Service
tblack      password5    Mechanic            Service
rbrown      password6    Body Tech           Service
sclark      password7    Loan Officer        Finance
pking       password8    Parts Clerk         Parts
nhall       password9    Receptionist        Administration
ayoung      password10   IT Specialist       IT


ROLE-BASED ACCESS
-----------------
Administrator  : All pages including Admin panel (user mgmt, divisions)
Sales (Div 1)  : Dashboard, Customers, Vehicles, Sales, Reports
Service (Div 2): Dashboard, Customers, Vehicles, Service, Reports
Finance (Div 3): Dashboard, Customers, Vehicles, Loans, Accounting, Reports
All roles      : Customers, Vehicles, Reports always visible


FUNCTIONAL REQUIREMENTS COVERAGE
---------------------------------
FR 1  User Auth         /  (login), /logout
FR 2  Org Structure     /admin/divisions, /admin/employees
FR 3  Customer Mgmt     /customers, /customers/new, /customers/<id>/edit
FR 4  Vehicle Mgmt      /vehicles, /vehicles/new, /vehicles/<id>/edit
FR 5  Sales Mgmt        /sales, /sales/new  (auto-updates vehicle status)
FR 6  Service Mgmt      /service, /service/new, /service/<id>/edit
FR 7  Loan Mgmt         /loans, /loans/new, /loans/<id>/payment
FR 8  Accounting        /accounting
FR 9  Reports           /reports/sales, /reports/service,
                        /reports/loans, /reports/accounting
FR 10 Search/Query      Search bars on customers, vehicles, sales, service
FR 11 Data Integrity    Enforced by DB constraints (see createDDL.sql)
