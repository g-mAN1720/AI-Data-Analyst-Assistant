import streamlit as st
import pandas as pd



# 🔥 Column type detection function
def detect_column_type(series, col_name):
    sample = series.dropna()

    if sample.empty:
        return "Unknown"

    # Name-based hints
    if "date" in col_name.lower():
        return "Datetime"
    if "id" in col_name.lower():
        return "Categorical"

    # Try numeric
    try:
        numeric = pd.to_numeric(sample)
        if (numeric % 1 == 0).all():
            return "Integer"
        else:
            return "Float"
    except:
        pass

    # Try datetime
    try:
        pd.to_datetime(sample)
        return "Datetime"
    except:
        pass

    return "String"

st.set_page_config(page_title="AI Data Analyst Assistant", layout="wide")

st.title("📊 AI Data Analyst Assistant")
st.write("Upload your dataset and analyze it easily.")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File uploaded successfully!")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 Dataset Preview")
            st.dataframe(df.head())

        with col2:
            st.subheader("📊 Dataset Info")
            st.write(f"Rows: {df.shape[0]}")
            st.write(f"Columns: {df.shape[1]}")
                # 🧠 Column Type Detection
            st.subheader("🧠 Column Types")
            col_types = []

            for col in df.columns:
                detected_type = detect_column_type(df[col], col)
                col_types.append((col, detected_type))

            types_df = pd.DataFrame(col_types, columns=["Column Name", "Detected Type"])

            st.dataframe(types_df, use_container_width=True)
# for entire column value 
            st.subheader("🔍 Column Explorer")
            selected_col = st.selectbox("Select a column", df.columns)

            col_data = df[[selected_col]]
            def highlight_issues(val):
                if pd.isna(val) or val == "":
                    return "background-color: red; color: white;"
                return ""
            styled_df = col_data.style.map(highlight_issues)

            st.dataframe(styled_df, use_container_width=True)   
            missing_count = col_data[selected_col].isna().sum()

            st.warning(f"⚠️ Missing Values: {missing_count}")
            st.markdown("---")
            st.header("🧪 Data Quality Checks")

            # ==============================
            # 1. Missing Values (Enhanced)
            # ==============================
            st.subheader("🧩 Missing Values")

            missing = df.isnull().sum()
            missing_pct = (missing / len(df)) * 100

            missing_df = pd.DataFrame({
                "Column": df.columns,
                "Missing Count": missing.values,
                "Missing %": missing_pct.values
            })

            missing_df = missing_df[missing_df["Missing Count"] > 0]

            if not missing_df.empty:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("✅ No missing values")

            # ==============================
            # 2. Duplicate Rows & Columns
            # ==============================
            st.subheader("🔁 Duplicates")

            dup_rows = df.duplicated().sum()
            st.write(f"Duplicate Rows: {dup_rows}")

            # Duplicate columns
            dup_cols = df.columns[df.columns.duplicated()].tolist()
            st.write(f"Duplicate Columns: {dup_cols if dup_cols else 'None'}")

            # ==============================
            # 3. Data Type Issues & Mixed Data
            # ==============================
            st.subheader("⚠️ Data Type Issues")

            type_issues = []

            for col in df.columns:
                if df[col].dtype == "object":
                    try:
                        pd.to_numeric(df[col])
                        type_issues.append((col, "Numeric stored as text"))
                    except:
                        pass

                    # Mixed type detection
                    unique_types = df[col].dropna().apply(type).nunique()
                    if unique_types > 1:
                        type_issues.append((col, "Mixed Data Types"))

            if type_issues:
                st.dataframe(pd.DataFrame(type_issues, columns=["Column", "Issue"]))
            else:
                st.success("✅ No major type issues")

            # ==============================
            # 4. Outlier Detection
            # ==============================
            st.subheader("📊 Outliers")

            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            outlier_data = []

            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]

                if len(outliers) > 0:
                    outlier_data.append((col, len(outliers)))

            if outlier_data:
                st.dataframe(pd.DataFrame(outlier_data, columns=["Column", "Outlier Count"]))
            else:
                st.success("✅ No outliers")

            # ==============================
            # 5. Invalid Values
            # ==============================
            st.subheader("🚫 Invalid Values")

            invalid_data = []

            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    if (df[col] < 0).any():
                        invalid_data.append((col, "Negative values found"))

                if df[col].dtype == "object":
                    if df[col].isin(["?", "NA", "null", "None", ""]).any():
                        invalid_data.append((col, "Contains invalid placeholders"))

            if invalid_data:
                st.dataframe(pd.DataFrame(invalid_data, columns=["Column", "Issue"]))
            else:
                st.success("✅ No obvious invalid values")

            # ==============================
            # 6. Extra Spaces
            # ==============================
            st.subheader("✂️ Extra Spaces")

            space_issues = []

            for col in df.select_dtypes(include="object").columns:
                if df[col].str.startswith(" ").any() or df[col].str.endswith(" ").any():
                    space_issues.append(col)

            if space_issues:
                st.write("Columns with extra spaces:", space_issues)
            else:
                st.success("✅ No extra spaces")

            # ==============================
            # 7. Date Format Issues
            # ==============================
            st.subheader("📅 Date Format Issues")

            date_issues = []

            for col in df.columns:
                if "date" in col.lower():
                    try:
                        pd.to_datetime(df[col], errors='coerce')
                        if pd.to_datetime(df[col], errors='coerce').isna().sum() > 0:
                            date_issues.append(col)
                    except:
                        date_issues.append(col)

            if date_issues:
                st.write("Columns with date issues:", date_issues)
            else:
                st.success("✅ No date issues")

            # ==============================
            # 8. Encoding / Text Issues (Basic)
            # ==============================
            st.subheader("🔤 Encoding Issues")

            encoding_issues = []

            for col in df.select_dtypes(include="object").columns:
                if df[col].str.contains(r"[^\x00-\x7F]", regex=True).any():
                    encoding_issues.append(col)

            if encoding_issues:
                st.write("Columns with possible encoding issues:", encoding_issues)
            else:
                st.success("✅ No encoding issues")
            
    except Exception as e:
      st.error(f"Error: {e}")