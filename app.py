
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="KOC Data Cleaner", layout="wide")
st.title("🧹 Công cụ chuẩn hoá dữ liệu KOC")

uploaded_file = st.file_uploader("Tải lên file dữ liệu (.csv hoặc .json)", type=["csv", "json"])

def parse_numeric(value):
    if isinstance(value, str):
        if "K" in value and "₫" not in value:
            return int(float(value.replace("K", "")) * 1000)
        if "M" in value and "₫" not in value:
            return int(float(value.replace("M", "")) * 1000000)
    return value

def standardize_row(row):
    to = row.get("totalOrders", "")
    gpm = row.get("gpm", "")
    aov = row.get("aov", "")

    if isinstance(to, str) and "₫" in to:
        if not aov:
            row["aov"] = to
            row["totalOrders"] = None

    if isinstance(gpm, str) and "₫" not in gpm:
        if not row.get("totalOrders"):
            row["totalOrders"] = parse_numeric(gpm)
            row["gpm"] = None

    if isinstance(aov, str) and "₫" in aov and not gpm:
        row["gpm"] = aov
        row["aov"] = None

    return row

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)

    df_cleaned = df.apply(standardize_row, axis=1)

    st.subheader("📊 Dữ liệu sau khi chuẩn hoá")
    st.dataframe(df_cleaned)

    st.download_button(
        label="📥 Tải file kết quả (.xlsx)",
        data=df_cleaned.to_excel(index=False, engine='openpyxl'),
        file_name="koc_cleaned_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
