import base64
import html
import os
import re
import urllib.parse
from google import genai
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="كلية علوم الحاسوب والرياضيات",
    page_icon="🏛️",
    layout="centered",
)


def get_logo_html(image_path="logo.png", width="85px"):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode()
        return f"<img src='data:image/png;base64,{b64_str}' style='width: {width}; height: {width}; object-fit: contain; border-radius: 50%; margin-bottom: 8px; box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);'>"
    return "<div style='font-size: 48px; margin-bottom: 5px;'>🏛️</div>"


logo_login_html = get_logo_html("logo.png", "95px")
logo_header_html = get_logo_html("logo.png", "65px")

css_style = (
    "<style>"
    ".stApp { background: radial-gradient(circle at top, #2c1810 0%, #160e0a 55%, #0e0907 100%) !important; }"
    "header { visibility: hidden !important; }"
    ".chat-box { display: flex; flex-direction: column; gap: 15px; padding: 20px; background: transparent !important; }"
    ".msg-wrapper { display: flex; width: 100%; }"
    ".msg-wrapper.assistant { justify-content: flex-end; }"
    ".msg-wrapper.user { justify-content: flex-start; }"
    ".bubble { padding: 14px 18px; border-radius: 18px; font-size: 16px; max-width: 82%; color: white; line-height: 1.6; }"
    ".assistant .bubble { background: linear-gradient(135deg, #f59e0b 0%, #ea580c 50%, #b91c1c 100%) !important; border-bottom-left-radius: 4px; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.35); }"
    ".assistant .bubble a { display: inline-block; margin-top: 6px; margin-bottom: 4px; padding: 6px 14px; background-color: #1c1008; color: #fbbf24 !important; text-decoration: none; border-radius: 8px; font-weight: bold; border: 1px solid #fbbf24; }"
    ".user .bubble { background-color: rgba(45, 28, 20, 0.85) !important; border: 1px solid #573322 !important; border-bottom-right-radius: 4px; backdrop-filter: blur(6px); }"
    "div[data-testid='stTextInput'] input { background-color: rgba(30, 19, 14, 0.9) !important; color: white !important; border: 1px solid #573322 !important; border-radius: 10px !important; }"
    "div[data-testid='stMetric'] { background-color: rgba(32, 20, 14, 0.75) !important; border: 1px solid #452718 !important; padding: 15px !important; border-radius: 14px !important; text-align: center !important; backdrop-filter: blur(6px); }"
    "div[data-testid='stMetricLabel'] { color: #e2cfc4 !important; font-size: 14px !important; }"
    "div[data-testid='stMetricValue'] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("يرجى ضبط مفتاح الـ API في إعدادات الأسرار.")
    st.stop()

SHEET_ID = "1Z1snF8YttXoUu1TA35jD8cfbKtX4uZYK2-h2kOVDSTk"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="


@st.cache_data(ttl=5)
def load_all_academic_data():
    default_subjects_info = {
        "math_eng": {"subject_name": "رياضيات هندسية", "professor": "لم يحدد بعد", "lectures": []},
        "group_theory": {"subject_name": "جبر الزمر", "professor": "لم يحدد بعد", "lectures": []},
        "fuzzy_math": {"subject_name": "رياضيات ضبابية", "professor": "لم يحدد بعد", "lectures": []},
        "arabic": {"subject_name": "اللغة العربية", "professor": "لم يحدد بعد", "lectures": []},
        "ai": {"subject_name": "الذكاء الاصطناعي", "professor": "لم يحدد بعد", "lectures": []},
        "operations_res": {"subject_name": "بحوث العمليات", "professor": "لم يحدد بعد", "lectures": []},
    }

    try:
        encoded_info = urllib.parse.quote("subjects_info")
        df_info = pd.read_csv(BASE_URL + encoded_info, dtype=str)
        df_info.columns = df_info.columns.str.strip()
        for _, row in df_info.iterrows():
            key = str(row.get("subject_key", "")).strip()
            if key in default_subjects_info:
                default_subjects_info[key]["subject_name"] = str(row.get("subject_name", default_subjects_info[key]["subject_name"])).strip()
                default_subjects_info[key]["professor"] = str(row.get("professor", "لم يحدد")).strip()
    except Exception:
        pass

    try:
        encoded_lec = urllib.parse.quote("lectures")
        df_lec = pd.read_csv(BASE_URL + encoded_lec, dtype=str)
        df_lec.columns = df_lec.columns.str.strip()
        for _, row in df_lec.iterrows():
            key = str(row.get("subject_key", "")).strip()
            title = str(row.get("lecture_title", "")).strip()
            url = str(row.get("lecture_url", "")).strip()
            if key in default_subjects_info and url.startswith("http"):
                default_subjects_info[key]["lectures"].append({"title": title, "url": url})
    except Exception:
        pass

    df_schedule = pd.DataFrame()
    try:
        encoded_sched = urllib.parse.quote("schedule")
        df_schedule = pd.read_csv(BASE_URL + encoded_sched, dtype=str)
        df_schedule.columns = df_schedule.columns.str.strip()
    except Exception:
        pass

    try:
        encoded_accounts = urllib.parse.quote("حسابات_الطلاب")
        final_df = pd.read_csv(BASE_URL + encoded_accounts, dtype=str)
        final_df.columns = final_df.columns.str.strip()
        if "username" in final_df.columns:
            final_df["username"] = final_df["username"].astype(str).str.strip()
    except Exception:
        return (
            pd.DataFrame([{"username": "111111", "password": "123", "student_name": "علي حكمت حسن"}]),
            default_subjects_info,
            df_schedule,
