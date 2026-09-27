-- =============================================================
-- createDDL.sql
-- Group 2 / Part 2 - Matthew, Jackson, Stephen, Ohm
-- Creates the GroupTwoDealership database and all tables with
-- primary keys, foreign keys, and CHECK/UNIQUE constraints.
-- =============================================================

-- Create and select the database
DROP DATABASE IF EXISTS GroupTwoDealership;
CREATE DATABASE GroupTwoDealership;
USE GroupTwoDealership;

-- -------------------------------------------------------------
-- Division  (parent of Department; circular FK removed)
-- -------------------------------------------------------------
CREATE TABLE Division (
    DivisionID   INT PRIMARY KEY,
    Name         VARCHAR(255) NOT NULL
);

-- -------------------------------------------------------------
-- Department  (child of Division)
-- -------------------------------------------------------------
CREATE TABLE Department (
    DepartmentID INT PRIMARY KEY,
    DivisionID   INT NOT NULL,
    Name         VARCHAR(255) NOT NULL,
    FOREIGN KEY (DivisionID) REFERENCES Division(DivisionID)
);

-- -------------------------------------------------------------
-- Customer
-- -------------------------------------------------------------
CREATE TABLE Customer (
    CustID   INT PRIMARY KEY,
    Name     VARCHAR(255) NOT NULL,
    Address  VARCHAR(255) NOT NULL,
    Email    VARCHAR(255) NOT NULL UNIQUE
);

-- -------------------------------------------------------------
-- CustomerPhoneNumbers  (multi-valued attribute for Customer)
-- -------------------------------------------------------------
CREATE TABLE CustomerPhoneNumbers (
    PhoneID     INT PRIMARY KEY,
    CustID      INT NOT NULL,
    PhoneNumber CHAR(10) NOT NULL UNIQUE,
    CHECK (PhoneNumber REGEXP '^[0-9]{10}$'),
    FOREIGN KEY (CustID) REFERENCES Customer(CustID)
);

-- -------------------------------------------------------------
-- EmployeeAccount
-- -------------------------------------------------------------
CREATE TABLE EmployeeAccount (
    EmployeeID   INT PRIMARY KEY,
    DepartmentID INT NOT NULL,
    Username     VARCHAR(255) NOT NULL UNIQUE,
    Password     VARCHAR(255) NOT NULL,
    Job          VARCHAR(255) NOT NULL,
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
);

-- -------------------------------------------------------------
-- VehicleManagement
-- -------------------------------------------------------------
CREATE TABLE VehicleManagement (
    VehicleID          INT PRIMARY KEY,
    VIN                VARCHAR(17) NOT NULL UNIQUE,
    Make               VARCHAR(255) NOT NULL,
    Model              VARCHAR(255) NOT NULL,
    Year               YEAR NOT NULL,
    Price              DECIMAL(9,2) NOT NULL CHECK (Price >= 0),
    Mileage            INT NOT NULL CHECK (Mileage >= 0),
    VehicleCondition   ENUM('new','used') NOT NULL,
    AvailabilityStatus ENUM('available','sold','pending') NOT NULL
);

-- -------------------------------------------------------------
-- SaleManagement
-- -------------------------------------------------------------
CREATE TABLE SaleManagement (
    SaleID          INT PRIMARY KEY,
    EmployeeID      INT NOT NULL,
    VehicleID       INT NOT NULL,
    CustID          INT NOT NULL,
    SalePrice       DECIMAL(9,2) NOT NULL CHECK (SalePrice >= 0),
    DateOfSale      DATE NOT NULL,
    PaymentMethod   ENUM('cash','card','check') NOT NULL,
    FinancingOption VARCHAR(255) NOT NULL,
    FOREIGN KEY (EmployeeID) REFERENCES EmployeeAccount(EmployeeID),
    FOREIGN KEY (VehicleID)  REFERENCES VehicleManagement(VehicleID),
    FOREIGN KEY (CustID)     REFERENCES Customer(CustID)
);

-- -------------------------------------------------------------
-- ServiceRecord
-- -------------------------------------------------------------
CREATE TABLE ServiceRecord (
    ServiceID    INT PRIMARY KEY,
    ServiceDate  DATE NOT NULL,
    ServicePrice DECIMAL(9,2) NOT NULL CHECK (ServicePrice >= 0),
    CustID       INT NOT NULL,
    VehicleID    INT NOT NULL,
    FOREIGN KEY (CustID)    REFERENCES Customer(CustID),
    FOREIGN KEY (VehicleID) REFERENCES VehicleManagement(VehicleID)
);

-- -------------------------------------------------------------
-- Part
-- -------------------------------------------------------------
CREATE TABLE Part (
    PartID   INT PRIMARY KEY,
    PartCost DECIMAL(9,2) NOT NULL CHECK (PartCost >= 0),
    Name     VARCHAR(255) NOT NULL
);

-- -------------------------------------------------------------
-- PartServices  (junction table: ServiceRecord <-> Part)
-- -------------------------------------------------------------
CREATE TABLE PartServices (
    ServiceID INT NOT NULL,
    PartID    INT NOT NULL,
    Quantity  INT NOT NULL CHECK (Quantity >= 0),
    PRIMARY KEY (ServiceID, PartID),
    FOREIGN KEY (ServiceID) REFERENCES ServiceRecord(ServiceID),
    FOREIGN KEY (PartID)    REFERENCES Part(PartID)
);

-- -------------------------------------------------------------
-- FinancialServicesAndLoanManagement
-- -------------------------------------------------------------
CREATE TABLE FinancialServicesAndLoanManagement (
    LoanID             INT PRIMARY KEY,
    CustID             INT NOT NULL,
    VehicleID          INT NOT NULL,
    LoanAmount         DECIMAL(9,2) NOT NULL CHECK (LoanAmount >= 0),
    InterestRate       DECIMAL(4,2) NOT NULL CHECK (InterestRate >= 0),
    LoanTerm           INT NOT NULL CHECK (LoanTerm > 0),
    MonthlyPayment     DECIMAL(9,2) NOT NULL CHECK (MonthlyPayment >= 0),
    LoanApprovalStatus ENUM('yes','no') NOT NULL,
    FOREIGN KEY (CustID)    REFERENCES Customer(CustID),
    FOREIGN KEY (VehicleID) REFERENCES VehicleManagement(VehicleID)
);

-- -------------------------------------------------------------
-- LoanServicePayments
-- -------------------------------------------------------------
CREATE TABLE LoanServicePayments (
    PaymentID     INT PRIMARY KEY,
    LoanID        INT NOT NULL,
    Name          VARCHAR(255) NOT NULL,
    DueDate       DATE NOT NULL,
    OwedAmount    DECIMAL(9,2) NOT NULL CHECK (OwedAmount >= 0),
    NextDueAmount DECIMAL(9,2) NOT NULL CHECK (NextDueAmount >= 0),
    FOREIGN KEY (LoanID) REFERENCES FinancialServicesAndLoanManagement(LoanID)
);

-- -------------------------------------------------------------
-- FinancialTransactions
-- SaleID/ServiceID/PaymentID are nullable; each transaction
-- references exactly ONE of the three source records.
-- -------------------------------------------------------------
CREATE TABLE FinancialTransactions (
    TransactionID   INT PRIMARY KEY,
    Amount          DECIMAL(20,2) NOT NULL,
    Date            DATE NOT NULL,
    SaleID          INT NULL,
    ServiceID       INT NULL,
    PaymentID       INT NULL,
    TransactionType VARCHAR(255) NOT NULL,
    CHECK (
        (SaleID IS NOT NULL) + (ServiceID IS NOT NULL) + (PaymentID IS NOT NULL) = 1
    ),
    FOREIGN KEY (SaleID)    REFERENCES SaleManagement(SaleID),
    FOREIGN KEY (ServiceID) REFERENCES ServiceRecord(ServiceID),
    FOREIGN KEY (PaymentID) REFERENCES LoanServicePayments(PaymentID)
);
