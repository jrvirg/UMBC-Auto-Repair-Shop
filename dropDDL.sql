-- =============================================================
-- dropDDL.sql
-- Group 2 / Part 2 - Matthew, Jackson, Stephen, Ohm
-- Cleanly resets the database by dropping all tables and the DB.
-- =============================================================

USE GroupTwoDealership;

SET FOREIGN_KEY_CHECKS = 0;

-- Drop children before parents (order is irrelevant with FK checks off,
-- but listed child-first anyway for clarity).
DROP TABLE IF EXISTS FinancialTransactions;
DROP TABLE IF EXISTS LoanServicePayments;
DROP TABLE IF EXISTS FinancialServicesAndLoanManagement;
DROP TABLE IF EXISTS PartServices;
DROP TABLE IF EXISTS Part;
DROP TABLE IF EXISTS ServiceRecord;
DROP TABLE IF EXISTS SaleManagement;
DROP TABLE IF EXISTS VehicleManagement;
DROP TABLE IF EXISTS EmployeeAccount;
DROP TABLE IF EXISTS CustomerPhoneNumbers;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS Division;

SET FOREIGN_KEY_CHECKS = 1;

-- Drop the database itself
DROP DATABASE IF EXISTS GroupTwoDealership;
