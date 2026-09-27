-- =============================================================
-- report.sql
-- Group 2 / Part 2 - Matthew, Jackson, Stephen, Ohm
-- Sample queries demonstrating joins, aggregations, and
-- constraint enforcement on the database.
--
-- Expected output is shown as comments after each query.
--
-- =============================================================

USE GroupTwoDealership;

-- -------------------------------------------------------------
-- Q1. Total sales revenue per employee (JOIN + GROUP BY + SUM)
--     Shows how well each salesperson is performing.
-- -------------------------------------------------------------

SELECT e.EmployeeID,
       e.Username,
       COUNT(s.SaleID)   AS NumSales,
       SUM(s.SalePrice)  AS TotalRevenue
FROM   EmployeeAccount e
JOIN   SaleManagement  s ON e.EmployeeID = s.EmployeeID
GROUP  BY e.EmployeeID, e.Username
ORDER  BY TotalRevenue DESC;

-- Expected output:
-- +------------+----------+----------+--------------+
-- | EmployeeID | Username | NumSales | TotalRevenue |
-- +------------+----------+----------+--------------+
-- |          1 | msmith   |        4 |     86300.00 |
-- |          3 | kwhite   |        3 |     85500.00 |
-- |          2 | jdoe     |        3 |     83500.00 |
-- +------------+----------+----------+--------------+


-- -------------------------------------------------------------
-- Q2. Total customer spend across BOTH vehicle sales and
--     service visits (LEFT JOINs + aggregation across two paths)
-- -------------------------------------------------------------

SELECT c.CustID,
       c.Name,
       COALESCE(SUM(s.SalePrice),0)    AS SalesSpend,
       COALESCE(SUM(sr.ServicePrice),0) AS ServiceSpend,
       COALESCE(SUM(s.SalePrice),0) +
       COALESCE(SUM(sr.ServicePrice),0) AS TotalSpend
FROM   Customer c
LEFT   JOIN SaleManagement s  ON c.CustID = s.CustID
LEFT   JOIN ServiceRecord  sr ON c.CustID = sr.CustID
GROUP  BY c.CustID, c.Name
ORDER  BY TotalSpend DESC;

-- Expected output (top rows):
-- +--------+---------------+------------+--------------+------------+
-- | CustID | Name          | SalesSpend | ServiceSpend | TotalSpend |
-- +--------+---------------+------------+--------------+------------+
-- |      2 | Bob Smith     |   76000.00 |       990.00 |   76990.00 |
-- |      1 | Alice Johnson |   48000.00 |       750.00 |   48750.00 |
-- |      7 | Grace Lee     |   38500.00 |        95.00 |   38595.00 |
-- |     10 | Jack Thomas   |   27500.00 |         0.00 |   27500.00 |
-- |      5 | Eve Martinez  |   27000.00 |       125.00 |   27125.00 |
-- |      6 | Frank Brown   |   24500.00 |       210.00 |   24710.00 |
-- |      9 | Ivy Anderson  |   19800.00 |       180.00 |   19980.00 |
-- |      4 | David Wilson  |   19500.00 |       320.00 |   19820.00 |
-- |      8 | Henry Taylor  |   18500.00 |       275.00 |   18775.00 |
-- |      3 | Carol Davis   |   18000.00 |        85.00 |   18085.00 |
-- +--------+---------------+------------+--------------+------------+


-- -------------------------------------------------------------
-- Q3. Most-used parts across all services
--     (Junction-table JOIN + SUM on computed column)
-- -------------------------------------------------------------

SELECT p.PartID,
       p.Name,
       SUM(ps.Quantity)              AS TotalQty,
       SUM(ps.Quantity * p.PartCost) AS TotalPartCost
FROM   Part p
JOIN   PartServices ps ON p.PartID = ps.PartID
GROUP  BY p.PartID, p.Name
ORDER  BY TotalQty DESC;

-- Expected output:
-- +--------+----------------------------+----------+---------------+
-- | PartID | Name                       | TotalQty | TotalPartCost |
-- +--------+----------------------------+----------+---------------+
-- |      5 | Spark Plug                 |        8 |        102.00 |
-- |      3 | Brake Pad Set              |        6 |        539.94 |
-- |     10 | Windshield Wiper Blade     |        4 |        128.00 |
-- |      2 | Oil Filter                 |        3 |         73.50 |
-- |      7 | Air Filter                 |        2 |         56.00 |
-- |      4 | Alternator                 |        2 |        310.00 |
-- |      8 | Battery Terminal           |        2 |        151.00 |
-- |      6 | Timing Belt Kit            |        1 |        450.00 |
-- |      9 | Catalytic Converter Gasket |        1 |        199.99 |
-- +--------+----------------------------+----------+---------------+


-- -------------------------------------------------------------
-- Q4. Approved-loan statistics by vehicle condition
--     (JOIN + WHERE filter + AVG aggregation)
-- -------------------------------------------------------------

SELECT v.VehicleCondition,
       COUNT(*)         AS NumLoans,
       AVG(l.InterestRate) AS AvgRate
FROM   FinancialServicesAndLoanManagement l
JOIN   VehicleManagement v ON l.VehicleID = v.VehicleID
WHERE  l.LoanApprovalStatus = 'yes'
GROUP  BY v.VehicleCondition;

-- Expected output:
-- +------------------+----------+----------+
-- | VehicleCondition | NumLoans | AvgRate  |
-- +------------------+----------+----------+
-- | used             |        8 | 5.406250 |
-- +------------------+----------+----------+


-- -------------------------------------------------------------
-- Q5. Vehicles that have BOTH sales records AND service records
--     (multi-table INNER JOIN with COUNT DISTINCT)
-- -------------------------------------------------------------

SELECT v.VehicleID,
       v.Make,
       v.Model,
       COUNT(DISTINCT s.SaleID)    AS Sales,
       COUNT(DISTINCT sr.ServiceID) AS Services
FROM   VehicleManagement v
JOIN   SaleManagement s  ON v.VehicleID = s.VehicleID
JOIN   ServiceRecord  sr ON v.VehicleID = sr.VehicleID
GROUP  BY v.VehicleID, v.Make, v.Model
ORDER  BY Services DESC;

-- Expected output:
-- +-----------+------------+--------+-------+----------+
-- | VehicleID | Make       | Model  | Sales | Services |
-- +-----------+------------+--------+-------+----------+
-- |         1 | Honda      | Accord |     2 |        3 |
-- |         3 | Ford       | F-150  |     2 |        3 |
-- |         5 | Nissan     | Altima |     2 |        2 |
-- |         8 | Volkswagen | Jetta  |     2 |        2 |
-- |        10 | Hyundai    | Tucson |     2 |        1 |
-- +-----------+------------+--------+-------+----------+


-- -------------------------------------------------------------
-- Q6. Monthly transaction summary by type
--     (DATE_FORMAT + GROUP BY on two columns)
-- -------------------------------------------------------------

SELECT DATE_FORMAT(Date, '%Y-%m') AS Month,
       TransactionType,
       COUNT(*)  AS N,
       SUM(Amount) AS Total
FROM   FinancialTransactions
GROUP  BY Month, TransactionType
ORDER  BY Month, TransactionType;

-- Expected output:
-- +---------+-----------------+---+----------+
-- | Month   | TransactionType | N | Total    |
-- +---------+-----------------+---+----------+
-- | 2025-03 | Vehicle Sale    | 1 | 24000.00 |
-- | 2025-04 | Service         | 1 |   150.00 |
-- | 2025-04 | Vehicle Sale    | 1 | 38000.00 |
-- | 2025-05 | Service         | 1 |   450.00 |
-- | 2025-06 | Vehicle Sale    | 1 | 19500.00 |
-- | 2025-07 | Loan Payment    | 1 |   452.50 |
-- | 2025-07 | Service         | 1 |   320.00 |
-- | 2025-07 | Vehicle Sale    | 1 | 27000.00 |
-- | 2025-08 | Loan Payment    | 2 |   865.40 |
-- | 2025-09 | Service         | 1 |   600.00 |
-- | 2025-10 | Loan Payment    | 1 |   704.55 |
-- +---------+-----------------+---+----------+


-- -------------------------------------------------------------
-- Q7. Customers with more than one phone number
--     (JOIN + HAVING filter on aggregate)
-- -------------------------------------------------------------

SELECT c.CustID,
       c.Name,
       COUNT(p.PhoneID) AS PhoneCount
FROM   Customer c
JOIN   CustomerPhoneNumbers p ON c.CustID = p.CustID
GROUP  BY c.CustID, c.Name
HAVING COUNT(p.PhoneID) > 1;

-- Expected output:
-- +--------+---------------+------------+
-- | CustID | Name          | PhoneCount |
-- +--------+---------------+------------+
-- |      1 | Alice Johnson |          2 |
-- |      3 | Carol Davis   |          2 |
-- +--------+---------------+------------+


-- =============================================================
-- CONSTRAINT VIOLATION TESTS
-- Each of the statements below SHOULD fail.
-- We commented out so this script still runs end-to-end;
-- uncomment a block to verify the constraint is enforced.
-- =============================================================

-- -------------------------------------------------------------
-- V1. CHECK constraint: PartCost must be >= 0
-- -------------------------------------------------------------
-- INSERT INTO Part (PartID, PartCost, Name) VALUES (999, -5.00, 'bad');
-- Expected error:
--   ERROR 4025 (23000): CONSTRAINT `Part.PartCost` failed
--   for `GroupTwoDealership`.`Part`

-- -------------------------------------------------------------
-- V2. FOREIGN KEY: CustID 999 does not exist in Customer
-- -------------------------------------------------------------
-- INSERT INTO CustomerPhoneNumbers (PhoneID, CustID, PhoneNumber)
-- VALUES (99, 999, '1112223333');
-- Expected error:
--   ERROR 1452 (23000): Cannot add or update a child row:
--   a foreign key constraint fails

-- -------------------------------------------------------------
-- V3. UNIQUE: duplicate customer email
-- -------------------------------------------------------------
-- INSERT INTO Customer (CustID, Name, Address, Email)
-- VALUES (11, 'Duplicate', 'X', 'alice@example.com');
-- Expected error:
--   ERROR 1062 (23000): Duplicate entry 'alice@example.com' for key 'Email'

-- -------------------------------------------------------------
-- V4. CHECK (regex): PhoneNumber must be exactly 10 digits
-- -------------------------------------------------------------
-- INSERT INTO CustomerPhoneNumbers (PhoneID, CustID, PhoneNumber)
-- VALUES (99, 1, '123');
-- Expected error:
--   ERROR 4025 (23000): CONSTRAINT ... failed
--   for `GroupTwoDealership`.`CustomerPhoneNumbers`

-- -------------------------------------------------------------
-- V5. ENUM: 'broken' is not a valid VehicleCondition
-- -------------------------------------------------------------
-- INSERT INTO VehicleManagement
--   (VehicleID, VIN, Make, Model, Year, Price, Mileage,
--    VehicleCondition, AvailabilityStatus)
-- VALUES (99, 'BADVIN99', 'x', 'y', 2020, 100, 0, 'broken', 'available');
-- Expected error:
--   ERROR 1265 (01000): Data truncated for column 'VehicleCondition'

-- -------------------------------------------------------------
-- V6. CHECK: a FinancialTransaction must reference exactly ONE
--     of SaleID / ServiceID / PaymentID (not two, not zero)
-- -------------------------------------------------------------
-- INSERT INTO FinancialTransactions
--   (TransactionID, Amount, Date, SaleID, ServiceID, PaymentID, TransactionType)
-- VALUES (99, 100, '2025-01-01', 1, 1, NULL, 'bad');
-- Expected error:
--   ERROR 4025 (23000): CONSTRAINT ... failed
--   for `GroupTwoDealership`.`FinancialTransactions`
