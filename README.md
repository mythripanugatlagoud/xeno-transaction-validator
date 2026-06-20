# Transaction Data Validation & Processing Platform

A web-based transaction data validation platform built using **Python**, **Pandas**, and **Streamlit**. The application validates transaction datasets, identifies data quality issues, generates a cleaned output file, and supports automatic CSV chunking for large datasets.

**Live Demo:** https://xeno-transaction-validator-fhn4w4f3xszdfgytocycuk.streamlit.app/

---

##  Project Overview

Organizations often receive transaction data from multiple sources with inconsistent formats and missing information. This application helps validate uploaded transaction datasets before they are processed further.

The platform performs:

- Phone number validation using configurable country-specific rules
- Date and time format validation
- Payment mode validation
- Missing value detection
- Duplicate record detection
- General data integrity checks
- Cleaned dataset generation
- Automatic splitting of large CSV files into smaller chunks

---

##  Features

### CSV Upload

- Upload transaction datasets in CSV format.
- Preview uploaded data before validation.

### Flexible Column Mapping

Different companies use different column names.

Instead of forcing users to rename columns, the application allows mapping of:

- Phone Number
- Date
- Time
- Payment Mode
- Amount

making the platform reusable across different datasets.

---

### Phone Number Validation

Supports configurable country-specific validation.

Example:

| Country | Required Length |
|----------|-----------------|
| India | 10 digits |
| Singapore | 8 digits |

Additional countries can easily be added by updating the configuration.

---

### Date & Time Validation

Validates common date formats.

Examples:

- DD-MM-YYYY
- YYYY-MM-DD
- MM/DD/YYYY

Also validates multiple time formats including:

- HH:MM
- HH:MM:SS
- 12-hour format (AM/PM)

---

### Payment Mode Validation

Checks whether payment mode belongs to the allowed list.

Example:

- UPI
- Credit Card
- Debit Card
- Cash
- Net Banking
- Wallet

---

### Validation Summary

Displays:

- Total Valid Records
- Total Invalid Records
- Missing Fields
- Duplicate Rows
- Invalid Phone Numbers
- Invalid Payment Modes

---

### Clean Dataset Generation

After validation, only valid records are retained.

Users can directly download the cleaned CSV.

---

###  Large File Processing

Large datasets are automatically divided into multiple CSV chunks for easier processing and download.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Regular Expressions (Regex)

---

##  Project Structure

```
.
├── app.py
├── requirements.txt
├── README.md
├── valid_transactions.csv
├── invalid_transactions.csv
├── company_transactions_validation_test.csv
└── large_transactions.csv
```

---

## Workflow

```
Upload CSV
      │
      ▼
Preview Dataset
      │
      ▼
Map Required Columns
      │
      ▼
Run Validation
      │
      ▼
Phone Validation
Date Validation
Time Validation
Payment Validation
Duplicate Detection
Missing Value Detection
      │
      ▼
Validation Summary
      │
      ▼
Generate Clean Dataset
      │
      ▼
Download CSV
```

---

## Future Improvements

Possible enhancements include:

- User authentication
- Database integration
- Dashboard analytics
- REST API support
- Export to Excel/PDF
- Custom validation rule editor
- Multi-language support
- Cloud storage integration

---

## Learning Outcomes

This project helped strengthen my understanding of:

- Data validation pipelines
- CSV processing using Pandas
- Streamlit application development
- File handling
- Regular Expressions
- Data cleaning techniques
- Deploying web applications using Streamlit Community Cloud

---

