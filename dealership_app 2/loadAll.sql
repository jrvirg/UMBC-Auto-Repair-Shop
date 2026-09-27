-- =============================================================
-- loadAll.sql
-- Group 2 / Part 2 - Matthew, Jackson, Stephen, Ohm
-- Populates GroupTwoDealership with >=10 tuples per relation.
-- Data is designed to exercise joins and aggregations.
-- =============================================================

USE GroupTwoDealership;

-- -------------------------------------------------------------
-- Division  (parent of Department)
-- -------------------------------------------------------------

INSERT INTO Division (DivisionID, Name) VALUES
 (1, 'Sales'),
 (2, 'Service'),
 (3, 'Finance'),
 (4, 'Parts'),
 (5, 'Administration'),
 (6, 'Marketing'),
 (7, 'IT'),
 (8, 'HR'),
 (9, 'Operations'),
 (10, 'Customer Relations');

-- -------------------------------------------------------------
-- Department
-- -------------------------------------------------------------

INSERT INTO Department (DepartmentID, DivisionID, Name) VALUES
 (1,  1, 'New Car Sales'),
 (2,  1, 'Used Car Sales'),
 (3,  2, 'Mechanical Service'),
 (4,  2, 'Body Shop'),
 (5,  3, 'Loan Processing'),
 (6,  4, 'Parts Counter'),
 (7,  5, 'Front Desk'),
 (8,  6, 'Advertising'),
 (9,  7, 'Tech Support'),
 (10, 8, 'Payroll');

-- -------------------------------------------------------------
-- Customer
-- -------------------------------------------------------------

INSERT INTO Customer (CustID, Name, Address, Email) VALUES
 (1,  'Alice Johnson',   '123 Oak St, Baltimore, MD',     'alice@example.com'),
 (2,  'Bob Smith',       '456 Maple Ave, Columbia, MD',   'bob@example.com'),
 (3,  'Carol Davis',     '789 Pine Rd, Towson, MD',       'carol@example.com'),
 (4,  'David Wilson',    '321 Elm Ln, Catonsville, MD',   'david@example.com'),
 (5,  'Eve Martinez',    '654 Birch Dr, Annapolis, MD',   'eve@example.com'),
 (6,  'Frank Brown',     '987 Cedar Ct, Ellicott City, MD','frank@example.com'),
 (7,  'Grace Lee',       '147 Walnut Way, Bethesda, MD',  'grace@example.com'),
 (8,  'Henry Taylor',    '258 Cherry Blvd, Rockville, MD','henry@example.com'),
 (9,  'Ivy Anderson',    '369 Spruce St, Frederick, MD',  'ivy@example.com'),
 (10, 'Jack Thomas',     '741 Ash Pl, Gaithersburg, MD',  'jack@example.com');

-- -------------------------------------------------------------
-- CustomerPhoneNumbers  (some customers have multiple numbers)
-- -------------------------------------------------------------

INSERT INTO CustomerPhoneNumbers (PhoneID, CustID, PhoneNumber) VALUES
 (1,  1, '4105551001'),
 (2,  1, '4105551002'),  -- Alice has 2 phones
 (3,  2, '4105552001'),
 (4,  3, '4105553001'),
 (5,  3, '4105553002'),  -- Carol has 2 phones
 (6,  4, '4105554001'),
 (7,  5, '4105555001'),
 (8,  6, '4105556001'),
 (9,  7, '4105557001'),
 (10, 8, '4105558001'),
 (11, 9, '4105559001'),
 (12, 10,'4105550001');

-- -------------------------------------------------------------
-- EmployeeAccount
-- -------------------------------------------------------------

INSERT INTO EmployeeAccount (EmployeeID, DepartmentID, Username, Password, Job) VALUES
 (1,  1, 'msmith',    'hashed_pw_01', 'Sales Associate'),
 (2,  1, 'jdoe',      'hashed_pw_02', 'Sales Associate'),
 (3,  2, 'kwhite',    'hashed_pw_03', 'Sales Manager'),
 (4,  3, 'lgreen',    'hashed_pw_04', 'Mechanic'),
 (5,  3, 'tblack',    'hashed_pw_05', 'Mechanic'),
 (6,  4, 'rbrown',    'hashed_pw_06', 'Body Tech'),
 (7,  5, 'sclark',    'hashed_pw_07', 'Loan Officer'),
 (8,  6, 'pking',     'hashed_pw_08', 'Parts Clerk'),
 (9,  7, 'nhall',     'hashed_pw_09', 'Receptionist'),
 (10, 9, 'ayoung',    'hashed_pw_10', 'IT Specialist');

-- -------------------------------------------------------------
-- VehicleManagement
-- -------------------------------------------------------------

INSERT INTO VehicleManagement
 (VehicleID, VIN, Make, Model, Year, Price, Mileage, VehicleCondition, AvailabilityStatus) VALUES
 (1,  '1HGCM82633A004351', 'Honda',     'Accord',   2022, 24500.00, 15000,  'used',      'sold'),
 (2,  '1HGCM82633A004352', 'Honda',     'Civic',    2024, 22000.00, 100,    'new',       'available'),
 (3,  '1FTFW1ET5DFC12345', 'Ford',      'F-150',    2023, 38500.00, 8000,   'used',      'sold'),
 (4,  '5YJ3E1EA7KF000316', 'Tesla',     'Model 3',  2024, 42990.00, 50,     'new',       'available'),
 (5,  'JN1AZ4EH9FM430001', 'Nissan',    'Altima',   2021, 18500.00, 45000,  'used',      'sold'),
 (6,  'WBAJB1C51CC123456', 'BMW',       '5 Series', 2023, 54000.00, 12000,  'used',      'pending'),
 (7,  '2T1BURHE0JC001234', 'Toyota',    'Corolla',  2024, 21500.00, 200,    'new',       'available'),
 (8,  '3VWDP7AJ5CM123789', 'Volkswagen','Jetta',    2022, 19800.00, 28000,  'used',      'sold'),
 (9,  '1G1ZD5ST7LF000777', 'Chevrolet', 'Malibu',   2024, 24990.00, 150,    'new',       'available'),
 (10, 'KM8J3CA46JU000888', 'Hyundai',   'Tucson',   2023, 27500.00, 18000,  'used',      'sold'),
 (11, 'JM1BL1L87C1600999', 'Mazda',     'CX-5',     2024, 29500.00, 75,     'new',       'available'),
 (12, '1GNKVGED8BJ111222', 'Chevrolet', 'Traverse', 2020, 22000.00, 60000,  'used',      'pending');

-- -------------------------------------------------------------
-- SaleManagement
-- -------------------------------------------------------------

INSERT INTO SaleManagement
 (SaleID, EmployeeID, VehicleID, CustID, SalePrice, DateOfSale, PaymentMethod, FinancingOption) VALUES
 (1,  1, 1,  1, 24000.00, '2025-03-15', 'card',  'N/A'),
 (2,  2, 3,  2, 38000.00, '2025-04-02', 'cash',  'N/A'),
 (3,  1, 5,  3, 18000.00, '2025-05-10', 'check', 'N/A'),
 (4,  3, 8,  4, 19500.00, '2025-06-20', 'card',  '36-month loan'),
 (5,  2, 10, 5, 27000.00, '2025-07-05', 'card',  '60-month loan'),
 (6,  1, 1,  6, 24500.00, '2025-08-11', 'cash',  'N/A'),     -- vehicle 1 resold? demo data
 (7,  3, 3,  7, 38500.00, '2025-09-18', 'card',  '48-month loan'),
 (8,  2, 5,  8, 18500.00, '2025-10-22', 'check', 'N/A'),
 (9,  1, 8,  9, 19800.00, '2025-11-30', 'card',  '36-month loan'),
 (10, 3, 10, 10,27500.00, '2026-01-12', 'cash',  'N/A');

-- -------------------------------------------------------------
-- ServiceRecord
-- -------------------------------------------------------------

INSERT INTO ServiceRecord (ServiceID, ServiceDate, ServicePrice, CustID, VehicleID) VALUES
 (1,  '2025-04-01', 150.00, 1, 1),
 (2,  '2025-05-15', 450.00, 2, 3),
 (3,  '2025-06-10', 85.00,  3, 5),
 (4,  '2025-07-22', 320.00, 4, 8),
 (5,  '2025-08-18', 125.00, 5, 10),
 (6,  '2025-09-05', 600.00, 1, 1),   -- Alice returns
 (7,  '2025-10-14', 210.00, 6, 1),
 (8,  '2025-11-01', 95.00,  7, 3),
 (9,  '2025-12-09', 275.00, 8, 5),
 (10, '2026-02-03', 180.00, 9, 8),
 (11, '2026-03-15', 540.00, 2, 3);

-- -------------------------------------------------------------
-- Part
-- -------------------------------------------------------------

INSERT INTO Part (PartID, PartCost, Name) VALUES
 (1,  3.99,   'Phillips Screw'),
 (2,  24.50,  'Oil Filter'),
 (3,  89.99,  'Brake Pad Set'),
 (4,  155.00, 'Alternator'),
 (5,  12.75,  'Spark Plug'),
 (6,  450.00, 'Timing Belt Kit'),
 (7,  28.00,  'Air Filter'),
 (8,  75.50,  'Battery Terminal'),
 (9,  199.99, 'Catalytic Converter Gasket'),
 (10, 32.00,  'Windshield Wiper Blade'),
 (11, 8.25,   'Lug Nut');

-- -------------------------------------------------------------
-- PartServices  (junction; each service uses 1-3 parts)
-- -------------------------------------------------------------

INSERT INTO PartServices (ServiceID, PartID, Quantity) VALUES
 (1,  2,  1),  -- oil filter
 (1,  7,  1),  -- air filter
 (2,  3,  2),  -- brake pads (front+rear)
 (2,  5,  4),  -- 4 spark plugs
 (3,  10, 2),  -- wiper blades
 (4,  4,  1),  -- alternator
 (4,  8,  2),  -- battery terminals
 (5,  2,  1),
 (6,  6,  1),  -- timing belt kit
 (6,  5,  4),
 (7,  3,  2),
 (8,  2,  1),
 (9,  9,  1),
 (10, 7,  1),
 (10, 10, 2),
 (11, 3,  2),
 (11, 4,  1);

-- -------------------------------------------------------------
-- FinancialServicesAndLoanManagement
-- -------------------------------------------------------------

INSERT INTO FinancialServicesAndLoanManagement
 (LoanID, CustID, VehicleID, LoanAmount, InterestRate, LoanTerm, MonthlyPayment, LoanApprovalStatus) VALUES
 (1,  4, 8,  15000.00, 5.50, 36, 452.50,  'yes'),
 (2,  5, 10, 22000.00, 4.75, 60, 412.90,  'yes'),
 (3,  7, 3,  30000.00, 6.00, 48, 704.55,  'yes'),
 (4,  9, 8,  16000.00, 5.25, 36, 481.20,  'yes'),
 (5,  1, 1,  20000.00, 7.00, 60, 396.02,  'no'),
 (6,  2, 3,  28000.00, 5.00, 48, 644.85,  'yes'),
 (7,  3, 5,  15500.00, 8.25, 36, 487.35,  'no'),
 (8,  6, 1,  19000.00, 4.90, 60, 357.81,  'yes'),
 (9,  8, 5,  14500.00, 6.75, 36, 445.20,  'yes'),
 (10, 10,10, 21000.00, 5.10, 48, 485.27,  'yes');

-- -------------------------------------------------------------
-- LoanServicePayments  (only approved loans get payments)
-- -------------------------------------------------------------

INSERT INTO LoanServicePayments
 (PaymentID, LoanID, Name, DueDate, OwedAmount, NextDueAmount) VALUES
 (1,  1, 'David Wilson',   '2025-07-20', 14547.50, 452.50),
 (2,  1, 'David Wilson',   '2025-08-20', 14095.00, 452.50),
 (3,  2, 'Eve Martinez',   '2025-08-05', 21587.10, 412.90),
 (4,  3, 'Grace Lee',      '2025-10-18', 29295.45, 704.55),
 (5,  4, 'Ivy Anderson',   '2025-12-30', 15518.80, 481.20),
 (6,  6, 'Bob Smith',      '2025-05-02', 27355.15, 644.85),
 (7,  8, 'Frank Brown',    '2025-09-11', 18642.19, 357.81),
 (8,  9, 'Henry Taylor',   '2025-11-22', 14054.80, 445.20),
 (9,  10,'Jack Thomas',    '2026-02-12', 20514.73, 485.27),
 (10, 2, 'Eve Martinez',   '2025-09-05', 21174.20, 412.90),
 (11, 3, 'Grace Lee',      '2025-11-18', 28590.90, 704.55),
 (12, 6, 'Bob Smith',      '2025-06-02', 26710.30, 644.85);

-- -------------------------------------------------------------
-- FinancialTransactions
-- Each row references EXACTLY ONE of SaleID, ServiceID, PaymentID.
-- -------------------------------------------------------------

INSERT INTO FinancialTransactions
 (TransactionID, Amount, Date, SaleID, ServiceID, PaymentID, TransactionType) VALUES
 (1,  24000.00, '2025-03-15', 1,    NULL, NULL, 'Vehicle Sale'),
 (2,  38000.00, '2025-04-02', 2,    NULL, NULL, 'Vehicle Sale'),
 (3,  150.00,   '2025-04-01', NULL, 1,    NULL, 'Service'),
 (4,  450.00,   '2025-05-15', NULL, 2,    NULL, 'Service'),
 (5,  452.50,   '2025-07-20', NULL, NULL, 1,    'Loan Payment'),
 (6,  452.50,   '2025-08-20', NULL, NULL, 2,    'Loan Payment'),
 (7,  19500.00, '2025-06-20', 4,    NULL, NULL, 'Vehicle Sale'),
 (8,  320.00,   '2025-07-22', NULL, 4,    NULL, 'Service'),
 (9,  412.90,   '2025-08-05', NULL, NULL, 3,    'Loan Payment'),
 (10, 704.55,   '2025-10-18', NULL, NULL, 4,    'Loan Payment'),
 (11, 27000.00, '2025-07-05', 5,    NULL, NULL, 'Vehicle Sale'),
 (12, 600.00,   '2025-09-05', NULL, 6,    NULL, 'Service');
