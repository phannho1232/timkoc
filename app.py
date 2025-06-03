import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="KOC Data Cleaner", layout="wide")
st.title("🧹 Công cụ chuẩn hoá dữ liệu KOC")

uploaded_file = st.file_uploader("Tải lên file dữ liệu (.csv hoặc .json)", type=["csv", "json"])

# ----- Hàm chuẩn hóa -----

def parse_money(value):
    if not isinstance(value, str):
        return value
    if "-" in value:
        parts = value.replace("₫", "").replace("đ", "").split("-")
        try:
            nums = [float(p.strip().replace("K", "").replace("M", "")) * (1e3 if "K" in p else 1e6) for p in parts]
            return sum(nums) / len(nums)
        except:
            return value
    else:
        try:
            num = float(value.replace("₫", "").replace("đ", "").replace("K", "").replace("M", ""))
            if "M" in value:
                return num * 1e6
            elif "K" in value:
                return num * 1e3
            else:
                return num
        except:
            return value

def clean_koc_data(df):
    df = df.copy()
    for col in ['gmv', 'gpm', 'aov', 'totalOrders']:
        df[col] = df[col].apply(parse_money)

    def reassign_fields(row):
        if isinstance(row["totalOrders"], float) and row["totalOrders"] > 1000 and not row["aov"]:
            row["aov"] = row["totalOrders"]
            row["totalOrders"] = None
        if isinstance(row["gpm"], float) and row["gpm"] > 1000 and not row["aov"]:
            row["aov"] = row["gpm"]
            row["gpm"] = None
        if isinstance(row["aov"], float) and row["aov"] < 1000 and not row["gpm"]:
            row["gpm"] = row["aov"]
            row["aov"] = None
        return row

    df = df.apply(reassign_fields, axis=1)
    return df

# ----- Xuất Excel -----
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ----- Giao diện xử lý -----
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)

    df_cleaned = clean_koc_data(df)

    st.subheader("📊 Dữ liệu sau khi chuẩn hoá")
    st.dataframe(df_cleaned)

    excel_data = convert_df_to_excel(df_cleaned)

    st.download_button(
        label="📥 Tải file kết quả (.xlsx)",
        data=excel_data,
        file_name="koc_cleaned_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
