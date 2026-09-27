#!/usr/bin/env python3
"""
setup_accounts.py
Run ONCE after createDDL.sql, loadAll.sql, and patch.sql have been imported.
Replaces all plaintext/placeholder passwords in EmployeeAccount and
Administrator with proper werkzeug pbkdf2:sha256 hashes.

Usage:
    python setup_accounts.py

Accounts created (username / password):
  Employees (from loadAll.sql):
    msmith   / password1      Sales Associate
    jdoe     / password2      Sales Associate
    kwhite   / password3      Sales Manager
    lgreen   / password4      Mechanic
    tblack   / password5      Mechanic
    rbrown   / password6      Body Tech
    sclark   / password7      Loan Officer
    pking    / password8      Parts Clerk
    nhall    / password9      Receptionist
    ayoung   / password10     IT Specialist
  Administrator:
    admin    / admin123
"""

from werkzeug.security import generate_password_hash
import mysql.connector

DB = dict(host="127.0.0.1", user="root",
          password="my-secret-pw", database="GroupTwoDealership", port=3306)

EMPLOYEES = [
    ('msmith',  'password1'),
    ('jdoe',    'password2'),
    ('kwhite',  'password3'),
    ('lgreen',  'password4'),
    ('tblack',  'password5'),
    ('rbrown',  'password6'),
    ('sclark',  'password7'),
    ('pking',   'password8'),
    ('nhall',   'password9'),
    ('ayoung',  'password10'),
]

ADMINS = [
    ('admin', 'admin123'),
]

conn   = mysql.connector.connect(**DB)
cursor = conn.cursor()

for username, password in EMPLOYEES:
    hashed = generate_password_hash(password)
    cursor.execute(
        "UPDATE EmployeeAccount SET Password=%s WHERE Username=%s",
        (hashed, username)
    )
    print(f"  hashed employee: {username}")

for username, password in ADMINS:
    hashed = generate_password_hash(password)
    cursor.execute(
        "UPDATE Administrator SET Password=%s WHERE Username=%s",
        (hashed, username)
    )
    print(f"  hashed admin: {username}")

conn.commit()
cursor.close()
conn.close()
print("\nAll passwords hashed. Ready to run app.py.")
