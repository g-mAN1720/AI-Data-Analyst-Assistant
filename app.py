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
           
            
    except Exception as e:
        st.error(f"Error: {e}")