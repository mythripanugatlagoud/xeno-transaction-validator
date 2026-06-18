"""
Xeno Implementation Internship — Part 4: AI Empowerment
Transaction Data Validation & Processing Platform

Built with Streamlit. Validates order-level, product-level, and payment-mode
transaction data with configurable country-specific phone rules, date/time
format checks, and general data integrity checks. Outputs a cleaned file
and auto-splits large datasets into chunks.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import io
import zipfile

# -----------------------------
# CONFIG: Country-specific phone rules (easily extendable)
# -----------------------------
COUNTRY_PHONE_RULES = {
    "India (+91)": {"code": "+91", "digits": 10},
    "Singapore (+65)": {"code": "+65", "digits": 8},
    "USA (+1)": {"code": "+1", "digits": 10},
    "UK (+44)": {"code": "+44", "digits": 10},
    "UAE (+971)": {"code": "+971", "digits": 9},
    "Australia (+61)": {"code": "+61", "digits": 9},
}

ACCEPTED_DATE_FORMATS = [
    "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
]
ACCEPTED_TIME_FORMATS = [
    "%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p",
]
ACCEPTED_PAYMENT_MODES = [
    "credit card", "debit card", "upi", "net banking", "cash on delivery",
    "wallet", "cod", "paypal", "bank transfer",
]

CHUNK_SIZE_ROWS = 5000  # rows per split chunk


# -----------------------------
# VALIDATION HELPERS
# -----------------------------
def validate_phone(value, digit_count):
    """Return True if value, stripped of non-digits, matches expected digit count.

    Handles the common case where pandas reads a numeric phone column as
    float64 (e.g. 9876543210 -> "9876543210.0"), which would otherwise corrupt
    the digit count by appending a trailing zero from the decimal point.
    """
    if pd.isna(value):
        return False
    if isinstance(value, float) and value.is_integer():
        s = str(int(value))
    else:
        s = str(value)
    digits = re.sub(r"\D", "", s)
    return len(digits) == digit_count


def validate_date(value):
    if pd.isna(value) or str(value).strip() == "":
        return False
    s = str(value).strip()
    for fmt in ACCEPTED_DATE_FORMATS:
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_time(value):
    if pd.isna(value) or str(value).strip() == "":
        return False
    s = str(value).strip()
    for fmt in ACCEPTED_TIME_FORMATS:
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_payment_mode(value):
    if pd.isna(value):
        return False
    return str(value).strip().lower() in ACCEPTED_PAYMENT_MODES


def validate_amount(value):
    """General integrity check for numeric amount fields: must be a non-negative number."""
    if pd.isna(value):
        return False
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False


def validate_email_basic(value):
    if pd.isna(value) or str(value).strip() == "":
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, str(value).strip()))


def run_validation(df, phone_col, date_col, time_col, payment_col, digit_count, amount_col=None):
    """
    Runs all validation checks and returns:
    - annotated dataframe (with _valid flag columns)
    - cleaned dataframe (only fully valid rows)
    - summary dict of issue counts
    """
    result = df.copy()
    issues = {}

    # Missing value check (any column entirely empty in a row)
    result["_missing_fields"] = result.isnull().any(axis=1)
    issues["Rows with missing fields"] = int(result["_missing_fields"].sum())

    # Duplicate check (based on all columns)
    result["_duplicate_row"] = result.duplicated(keep="first")
    issues["Duplicate rows"] = int(result["_duplicate_row"].sum())

    valid_mask = ~result["_duplicate_row"]

    if phone_col and phone_col in result.columns:
        result["_phone_valid"] = result[phone_col].apply(
            lambda v: validate_phone(v, digit_count)
        )
        issues["Invalid phone numbers"] = int((~result["_phone_valid"]).sum())
        valid_mask &= result["_phone_valid"]

    if date_col and date_col in result.columns:
        result["_date_valid"] = result[date_col].apply(validate_date)
        issues["Invalid dates"] = int((~result["_date_valid"]).sum())
        valid_mask &= result["_date_valid"]

    if time_col and time_col in result.columns:
        result["_time_valid"] = result[time_col].apply(validate_time)
        issues["Invalid times"] = int((~result["_time_valid"]).sum())
        valid_mask &= result["_time_valid"]

    if payment_col and payment_col in result.columns:
        result["_payment_valid"] = result[payment_col].apply(validate_payment_mode)
        issues["Invalid payment modes"] = int((~result["_payment_valid"]).sum())
        valid_mask &= result["_payment_valid"]

    if amount_col and amount_col in result.columns:
        result["_amount_valid"] = result[amount_col].apply(validate_amount)
        issues["Invalid/negative amounts"] = int((~result["_amount_valid"]).sum())
        valid_mask &= result["_amount_valid"]

    result["_row_valid"] = valid_mask & ~result["_missing_fields"]
    issues["Total valid rows"] = int(result["_row_valid"].sum())
    issues["Total invalid rows"] = int((~result["_row_valid"]).sum())

    cleaned = df[result["_row_valid"].values].copy()

    return result, cleaned, issues


def split_into_chunks(df, chunk_size=CHUNK_SIZE_ROWS):
    """Split a dataframe into a list of (filename, csv_bytes) chunks."""
    chunks = []
    total_rows = len(df)
    num_chunks = max(1, (total_rows + chunk_size - 1) // chunk_size)
    for i in range(num_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, total_rows)
        chunk_df = df.iloc[start:end]
        buf = io.StringIO()
        chunk_df.to_csv(buf, index=False)
        chunks.append((f"cleaned_chunk_{i+1}.csv", buf.getvalue().encode("utf-8")))
    return chunks


def df_to_zip_bytes(chunks):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, data in chunks:
            zf.writestr(filename, data)
    return zip_buf.getvalue()


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Transaction Data Validator", layout="wide")

st.title("Transaction Data Validation & Processing Platform")
st.caption(
    "Upload a transaction dataset (order, product, and payment details) to validate "
    "phone numbers, dates, times, and payment modes — then download a cleaned file."
)

with st.sidebar:
    st.header("Configuration")
    country = st.selectbox("Phone Number Country Rule", list(COUNTRY_PHONE_RULES.keys()))
    digit_count = COUNTRY_PHONE_RULES[country]["digits"]
    st.caption(f"Expecting **{digit_count}-digit** phone numbers for {country}.")

    st.markdown("---")
    st.markdown("**Accepted date formats:**")
    st.code("\n".join(ACCEPTED_DATE_FORMATS), language=None)
    st.markdown("**Accepted time formats:**")
    st.code("\n".join(ACCEPTED_TIME_FORMATS), language=None)
    st.markdown("**Accepted payment modes:**")
    st.caption(", ".join(ACCEPTED_PAYMENT_MODES))

uploaded_file = st.file_uploader("Upload transaction CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.success(f"Loaded **{len(df)}** rows and **{len(df.columns)}** columns.")
    with st.expander("Preview uploaded data", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)

    st.markdown("### Map Your Columns")
    st.caption("Tell us which columns correspond to phone, date, time, and payment mode.")

    cols = ["(none)"] + list(df.columns)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        phone_col = st.selectbox("Phone column", cols, key="phone")
    with c2:
        date_col = st.selectbox("Date column", cols, key="date")
    with c3:
        time_col = st.selectbox("Time column", cols, key="time")
    with c4:
        payment_col = st.selectbox("Payment mode column", cols, key="payment")
    with c5:
        amount_col = st.selectbox("Amount column", cols, key="amount")

    phone_col = None if phone_col == "(none)" else phone_col
    date_col = None if date_col == "(none)" else date_col
    time_col = None if time_col == "(none)" else time_col
    payment_col = None if payment_col == "(none)" else payment_col
    amount_col = None if amount_col == "(none)" else amount_col

    if st.button(" Run Validation", type="primary"):
        with st.spinner("Validating data..."):
            annotated, cleaned, issues = run_validation(
                df, phone_col, date_col, time_col, payment_col, digit_count, amount_col
            )

        st.markdown("###  Validation Summary")
        summary_cols = st.columns(len(issues))
        for (label, value), col in zip(issues.items(), summary_cols):
            col.metric(label, value)

        st.markdown("###  Detailed Results (flagged rows highlighted)")
        flag_cols = [c for c in annotated.columns if c.startswith("_")]
        display_df = annotated.copy()
        st.dataframe(
            display_df.style.apply(
                lambda row: [
                    "background-color: #ffe5e5" if not row["_row_valid"] else ""
                    for _ in row
                ],
                axis=1,
            ),
            use_container_width=True,
            height=350,
        )

        st.markdown("###Cleaned Dataset")
        st.write(f"**{len(cleaned)}** of **{len(df)}** rows passed all checks.")
        st.dataframe(cleaned.head(20), use_container_width=True)

        st.markdown("### ⬇️ Download")
        dl1, dl2 = st.columns(2)

        with dl1:
            csv_buf = io.StringIO()
            cleaned.to_csv(csv_buf, index=False)
            st.download_button(
                "Download Cleaned CSV (full file)",
                data=csv_buf.getvalue(),
                file_name="cleaned_transactions.csv",
                mime="text/csv",
            )

        with dl2:
            if len(cleaned) > CHUNK_SIZE_ROWS:
                chunks = split_into_chunks(cleaned)
                zip_bytes = df_to_zip_bytes(chunks)
                st.download_button(
                    f"Download Split Chunks (ZIP, {len(chunks)} files)",
                    data=zip_bytes,
                    file_name="cleaned_transactions_chunks.zip",
                    mime="application/zip",
                )
            else:
                st.caption(
                    f"File has {len(cleaned)} rows (≤ {CHUNK_SIZE_ROWS}), "
                    "so no chunk-splitting needed."
                )

else:
    st.info("👆 Upload a CSV file to get started.")
    st.markdown("#### Expected columns (example)")
    sample = pd.DataFrame({
        "order_id": [1001, 1002],
        "product_name": ["Wireless Mouse", "USB Cable"],
        "phone": ["9876543210", "98123456"],
        "order_date": ["2025-04-12", "12/04/2025"],
        "order_time": ["14:30:00", "2:30 PM"],
        "payment_mode": ["UPI", "Credit Card"],
        "amount": [499.0, 199.0],
    })
    st.dataframe(sample, use_container_width=True)
