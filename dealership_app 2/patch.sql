-- =============================================================
-- patch.sql
-- Run AFTER createDDL.sql + loadAll.sql
-- Adds Administrator table, fixes auto-increment PKs, and
-- re-hashes all employee passwords using werkzeug pbkdf2:sha256.
-- =============================================================

USE GroupTwoDealership;

SET FOREIGN_KEY_CHECKS = 0;

-- -------------------------------------------------------------
-- Make primary keys auto-increment so INSERT can omit them
-- -------------------------------------------------------------
ALTER TABLE Division        MODIFY DivisionID   INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Department      MODIFY DepartmentID INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Customer        MODIFY CustID       INT NOT NULL AUTO_INCREMENT;
ALTER TABLE CustomerPhoneNumbers MODIFY PhoneID INT NOT NULL AUTO_INCREMENT;
ALTER TABLE EmployeeAccount MODIFY EmployeeID   INT NOT NULL AUTO_INCREMENT;
ALTER TABLE VehicleManagement    MODIFY VehicleID  INT NOT NULL AUTO_INCREMENT;
ALTER TABLE SaleManagement       MODIFY SaleID     INT NOT NULL AUTO_INCREMENT;
ALTER TABLE ServiceRecord        MODIFY ServiceID  INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Part                 MODIFY PartID     INT NOT NULL AUTO_INCREMENT;
ALTER TABLE FinancialServicesAndLoanManagement MODIFY LoanID INT NOT NULL AUTO_INCREMENT;
ALTER TABLE LoanServicePayments  MODIFY PaymentID  INT NOT NULL AUTO_INCREMENT;
ALTER TABLE FinancialTransactions MODIFY TransactionID INT NOT NULL AUTO_INCREMENT;

SET FOREIGN_KEY_CHECKS = 1;

-- -------------------------------------------------------------
-- Administrator table (separate from EmployeeAccount so that
-- admins are not tied to any department)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Administrator (
    AdminID  INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL
);

-- Default admin account — password will be re-set by setup_accounts.py
-- Placeholder value here; setup_accounts.py overwrites it with a hash.
INSERT IGNORE INTO Administrator (Username, Password)
VALUES ('admin', 'placeholder');

-- -------------------------------------------------------------
-- CustomerAccount  (allows customers to log in to the portal)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CustomerAccount (
    AccountID INT PRIMARY KEY AUTO_INCREMENT,
    CustID    INT NOT NULL,
    Username  VARCHAR(255) NOT NULL UNIQUE,
    Password  VARCHAR(255) NOT NULL,
    FOREIGN KEY (CustID) REFERENCES Customer(CustID)
);
