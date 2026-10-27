# Soko Fresh Multi-File Data Processing Pipeline

## Overview

Soko Fresh Supermarkets operates branches across Kenya and receives daily transaction exports from branch point-of-sale (POS) systems.

The objective of this project is to build a Python data pipeline that automatically discovers transaction files, validates data quality, cleans valid records, rejects problematic records with clear reasons, and generates a consolidated dataset for reporting.

This project simulates a real-world ETL (Extract, Transform, Load) workflow where incoming data cannot always be trusted and must be validated before being used for business reporting.

---

## Business Problem

Finance teams depend on daily transaction reports generated from CSV files submitted by different branches.

However, real data often contains issues such as:

- Missing values
- Invalid numeric fields
- Duplicate transaction IDs
- Inconsistent file structures
- Changes introduced by software upgrades

The pipeline ensures that only trustworthy records are included in reporting while maintaining a complete audit trail of rejected records.

---

## Project Objectives

The pipeline performs the following tasks:

✅ Discover transaction files automatically

✅ Read and process multiple CSV files

✅ Validate file structure against required columns

✅ Detect missing values

✅ Detect invalid quantities and prices

✅ Detect duplicate transaction IDs across all files

✅ Clean and standardize valid records

✅ Generate calculated line totals

✅ Consolidate all valid transactions

✅ Separate rejected transactions with rejection reasons

✅ Produce an operational processing summary

✅ Generate execution logs

---

## Project Structure

```text
day2-multi-file-pipeline/
│
├── data/
│   ├── transactions_2026-10-01.csv
│   ├── transactions_2026-10-02.csv
│   └── transactions_2026-10-03.csv
│
├── output/
│   ├── consolidated_transactions.csv
│   ├── rejected_transactions.csv
│   └── summary.txt
│
├── pipeline.py
├── pipeline.log
├── requirements.txt
├── README.md
├── pyproject.toml
└── .gitignore
```

---

## ETL Workflow

### 1. Extract

The pipeline automatically discovers transaction files within the data directory using:

```python
Path.glob()
```

Each file is read using:

```python
csv.DictReader()
```

---

### 2. Transform

Records are validated and cleaned by:

- Removing extra whitespace
- Converting numeric fields to integers
- Calculating line totals
- Standardizing row structure

Example:

```python
line_total = quantity * unit_price
```

---

### 3. Load

Clean records are written to:

```text
output/consolidated_transactions.csv
```

Rejected records are written to:

```text
output/rejected_transactions.csv
```

A processing summary is saved to:

```text
output/summary.txt
```

---

## Validation Rules

### Required Columns

Every file must contain:

```text
transaction_id
date
branch
customer_id
product
quantity
unit_price
payment_method
```

---

### Missing Values

Rows are rejected when any required field is blank.

---

### Invalid Numbers

Rows are rejected when:

```text
quantity <= 0
```

or

```text
unit_price <= 0
```

or when values cannot be converted to numbers.

---

### Duplicate Transactions

Transaction IDs must be unique across the entire pipeline run.

If duplicate transaction IDs are encountered:

- The first valid occurrence is kept
- Subsequent occurrences are rejected

---

## Logging

Pipeline activity is recorded in:

```text
pipeline.log
```

Examples include:

- Files discovered
- Files processed
- Rejected records
- Summary statistics
- Processing completion status

This provides traceability and makes troubleshooting easier.

---

## Output Files

### Consolidated Transactions

```text
output/consolidated_transactions.csv
```

Contains:

- All valid transactions
- Calculated line totals
- Source file tracking

---

### Rejected Transactions

```text
output/rejected_transactions.csv
```

Contains:

- Original record
- Source file
- Row number
- Rejection reason(s)

This ensures that no data disappears silently.

---

### Processing Summary

```text
output/summary.txt
```

Contains:

- Files processed
- Rows read
- Accepted records
- Rejected records
- Duplicate counts
- Revenue totals
- Timestamp

---

## Technologies Used

- Python 3
- CSV Module
- Pathlib
- Logging
- Sets
- Dictionaries
- List/Dictionary Comprehensions
- Command-Line Arguments (argparse)
- uv (Python package manager)

---

## Key Python Concepts Demonstrated

- File handling
- CSV processing
- Functions
- Loops
- Conditionals
- Sets
- Dictionaries
- Comprehensions
- Data validation
- Logging
- ETL pipeline design

---

## Run the Pipeline

```bash
python pipeline.py --input data --output output
```

---

## Sample Workflow

```text
CSV Files
    │
    ▼
Discover Files
    │
    ▼
Read Data
    │
    ▼
Validate Schema
    │
    ▼
Validate Records
    │
    ▼
Clean Data
    │
    ▼
Calculate Totals
    │
    ▼
Separate Accepted and Rejected Records
    │
    ▼
Generate Outputs
    │
    ▼
Create Summary & Logs
```

---

## Outcomes
The project demonstrates how production data pipelines:

- Automatically ingest files
- Validate data quality
- Prevent duplicate records
- Maintain auditability
- Produce business-ready outputs
- Generate operational logs

These concepts form the foundation for larger ETL workflows.