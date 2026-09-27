-- =============================================================
-- migrate_v2.sql
-- Run this ONCE after patch.sql to add:
--   1. CustomerAccount table (customer portal logins)
--   2. IsActive column on EmployeeAccount (activate/deactivate)
-- =============================================================

USE GroupTwoDealership;

-- -------------------------------------------------------------
-- CustomerAccount
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CustomerAccount (
    AccountID INT PRIMARY KEY AUTO_INCREMENT,
    CustID    INT NOT NULL,
    Username  VARCHAR(255) NOT NULL UNIQUE,
    Password  VARCHAR(255) NOT NULL,
    FOREIGN KEY (CustID) REFERENCES Customer(CustID)
);

-- -------------------------------------------------------------
-- Employee active/inactive status
-- -------------------------------------------------------------
ALTER TABLE EmployeeAccount
    ADD COLUMN IF NOT EXISTS IsActive TINYINT NOT NULL DEFAULT 1;
