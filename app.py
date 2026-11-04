
import streamlit as st
import pandas as pd
import requests
import json
from pathlib import Path
from io import BytesIO

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="DataFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PROJECT_ROOT = Path(__file__).resolve().parent


# ==========================================
# 2. CUSTOM DARK THEME
# ==========================================

st.markdown("""
<style>

/* Background */

.stApp {
    background-color: #0b1120;
    color: #e2e8f0;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Top header */

header[data-testid="stHeader"] {
    background: #0b1120 !important;
    border-bottom: 1px solid #1e293b;
}

[data-testid="stSidebar"] {
    display: none;
}

/* Text */

h1, h2, h3, p, label {
    color: #e2e8f0;
}

/* Navbar */

.navbar {
    background: #101827;
    border: 1px solid #263449;
    border-radius: 13px;
    padding: 15px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 35px;
}

.brand {
    color: #f8fafc;
    font-size: 23px;
    font-weight: 800;
}

.brand-sub {
    color: #94a3b8;
    font-size: 12px;
}

.status {
    color: #4ade80;
    font-size: 12px;
    font-weight: 700;
}

/* Main heading */

.page-title {
    color: #f8fafc;
    font-size: 29px;
    font-weight: 800;
    margin-bottom: 5px;
}

.page-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 25px;
}

/* Cards */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111c2d;
    border: 1px solid #263449;
    border-radius: 15px;
    padding: 20px;
    transition: border-color 0.25s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #3b82f6;
}

.card-title {
    font-size: 18px;
    font-weight: 700;
    color: #f1f5f9;
}

/* File uploader */

[data-testid="stFileUploader"] {
    background: #0b1423;
    border: 1px dashed #38516e;
    border-radius: 10px;
    padding: 12px;
}

/* Input */

.stTextInput input {
    background: #0b1423 !important;
    color: white !important;
    border: 1px solid #334155 !important;
    border-radius: 9px !important;
}

/* Buttons */

.stButton button,
.stDownloadButton button {
    width: 100%;
    min-height: 43px;
    color: white !important;
    background: linear-gradient(100deg, #3b82f6, #6258e8);
    border: none;
    border-radius: 9px;
    font-weight: 700;
    transition: all 0.25s ease;
}

.stButton button:hover,
.stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 18px rgba(59,130,246,0.3);
}

/* Metrics */

[data-testid="stMetric"] {
    background: #111c2d;
    border: 1px solid #263449;
    border-radius: 12px;
    padding: 15px;
}

[data-testid="stMetricValue"] {
    color: #60a5fa;
}

/* Data table */

[data-testid="stDataFrame"] {
    border: 1px solid #263449;
    border-radius: 10px;
}

/* Divider */

hr {
    border-color: #263449;
}

/* Animation */

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main {
    animation: fadeIn 0.5s ease;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. TOP NAVIGATION
# ==========================================

st.markdown("""
<div class="navbar">
    <div>
        <div class="brand">⚡ DataFlow</div>
        <div class="brand-sub">Data Processing Pipeline</div>
    </div>
    <div class="status">● Pipeline Ready</div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. PAGE HEADING
# ==========================================

st.markdown("""
<div class="page-title">Process Dataset</div>
<div class="page-subtitle">
Upload a CSV/JSON file or provide an API endpoint.
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. READ DATA
# ==========================================

def read_uploaded_file(uploaded_file):

    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)

    data = json.load(uploaded_file)

    if isinstance(data, dict):
        data = data.get("data", data.get("results", [data]))

    return pd.DataFrame(data)


def read_api_data(url):

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict):
        data = data.get("data", data.get("results", [data]))

    return pd.DataFrame(data)


# ==========================================
# 6. DATA CLEANING
# ==========================================

def clean_data(df):

    df = df.copy()

    if df.empty:
        raise ValueError("Input data contains no records.")

    df.columns = df.columns.str.strip()

    required_columns = [
        "id", "name", "age", "salary", "city"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove extra spaces from text
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()

    # Replace empty strings with missing values
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # Fill missing names
    df["name"] = df["name"].fillna("Unknown")

    # Handle missing numeric values
    for column in ["age", "salary"]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if df[column].isna().all():
            raise ValueError(
                f"All values in {column} are missing or invalid."
            )

        median_value = df[column].median()

        df[column] = df[column].fillna(median_value)

    # Remove duplicates
    df = df.drop_duplicates()

    return df


# ==========================================
# 7. DATA TRANSFORMATION
# ==========================================

def transform_data(df):

    df = df.copy()

    df["age"] = df["age"].round().astype(int)
    df["salary"] = df["salary"].round().astype(int)

    def salary_category(salary):

        if salary < 30000:
            return "Low"

        elif salary < 40000:
            return "Medium"

        return "High"

    df["salary_category"] = df["salary"].apply(
        salary_category
    )

    return df


# ==========================================
# 8. COMPLETE PIPELINE
# ==========================================

def run_pipeline(df):

    cleaned_df = clean_data(df)

    final_df = transform_data(cleaned_df)

    return final_df


# ==========================================
# 9. UPLOAD AND API SECTION
# ==========================================

left, right = st.columns(2, gap="large")


# ------------------------------------------
# UPLOAD FILE
# ------------------------------------------

with left:

    with st.container(border=True):

        st.markdown(
            '<div class="card-title">📁 Upload File</div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Choose CSV or JSON",
            type=["csv", "json"],
            key="upload_file"
        )

        if uploaded_file:
            st.caption("Selected: " + uploaded_file.name)

        if st.button(
            "Process File",
            key="file_button",
            use_container_width=True
        ):

            if uploaded_file is None:

                st.warning("Please select a file first.")

            else:

                try:

                    df = read_uploaded_file(uploaded_file)

                    with st.spinner("Processing your data..."):
                        final_df = run_pipeline(df)

                    st.session_state["final_df"] = final_df
                    st.session_state["input_count"] = len(df)
                    st.session_state["output_count"] = len(final_df)

                    st.success("File processed successfully!")

                except Exception as error:

                    st.error(f"Processing failed: {error}")


# ------------------------------------------
# PROCESS API
# ------------------------------------------

with right:

    with st.container(border=True):

        st.markdown(
            '<div class="card-title">🌐 Process API</div>',
            unsafe_allow_html=True
        )

        api_url = st.text_input(
            "API Endpoint",
            placeholder="https://api.example.com/data",
            label_visibility="collapsed"
        )

        if st.button(
            "Process API",
            key="api_button",
            use_container_width=True
        ):

            if not api_url.strip():

                st.warning("Please enter an API endpoint.")

            else:

                try:

                    with st.spinner("Fetching API data..."):

                        df = read_api_data(api_url.strip())

                        final_df = run_pipeline(df)

                    st.session_state["final_df"] = final_df
                    st.session_state["input_count"] = len(df)
                    st.session_state["output_count"] = len(final_df)

                    st.success("API data processed successfully!")

                except requests.exceptions.RequestException as error:

                    st.error(f"API connection failed: {error}")

                except Exception as error:

                    st.error(f"Processing failed: {error}")


# ==========================================
# 10. DATA PREVIEW
# ==========================================

st.divider()

st.subheader("📊 Data Preview")

if "final_df" in st.session_state:

    final_df = st.session_state["final_df"]

    col1, col2 = st.columns(2)

    col1.metric(
        "Input Records",
        st.session_state["input_count"]
    )

    col2.metric(
        "Processed Records",
        st.session_state["output_count"]
    )

    st.dataframe(
        final_df,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # 11. DOWNLOAD RESULTS
    # ======================================

    st.subheader("Download Processed Data")

    csv_data = final_df.to_csv(index=False).encode("utf-8")

    json_data = final_df.to_json(
        orient="records",
        indent=4
    ).encode("utf-8")

    download1, download2 = st.columns(2)

    with download1:

        st.download_button(
            "⬇ Download CSV",
            data=csv_data,
            file_name="cleaned_employees.csv",
            mime="text/csv"
        )

    with download2:

        st.download_button(
            "⬇ Download JSON",
            data=json_data,
            file_name="cleaned_employees.json",
            mime="application/json"
        )

else:

    st.info(
        "Upload a file or provide an API endpoint to preview processed data."
    )
