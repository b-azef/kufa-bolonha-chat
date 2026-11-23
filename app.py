import re
import urllib.parse
from google import genai
import pandas as pd
import streamlit as st

# 1. إعدادات المظهر المظلم الكامل والمستقر
st.set_page_config(
    page_ttitle"كلية علوم الحاسوب والرياضيات",
    page_icon="🏛️",
    layout="centered",
)

# 🎨 تخصيص الألوان
st.markdown(
    """
<style>
    .stApp { background-color: #090d16 !important; }
    header { visibility: hidden !important; }
    .chat-box { display: flex; flex-direction: column; gap: 15px; padding: 20px; background-color: #090d16 !important; }
    .msg-wrapper { display: flex; width: 100%; }
    .msg-wrapper.assistant { justify-content: flex-end; }
    .msg-wrapper.user { justify-content: flex-start; }
    .bubble { padding: 14px 18px; border-radius: 18px; font-size: 16px; max-width: 82%; color: white; line-height: 1.6; }
    
    /* لون رسالة المساعد (برتقالي أكاديمي متدرج) */
    .assistant .bubble { 
        background: linear-gradient(135deg, #FFB347 40%, #0ea5e9 100%) !important; 
        border-bottom-left-radius: 4px; 
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25); 
    }
    
    /* تنسيق زر تحميل الملزمة داخل فقاعة المساعد */
    .assistant .bubble a {
        display: inline-block;
        margin-top: 8px;
        padding: 6px 14px;
        background-color: #0f172a;
        color: #38bdf8 !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #38bdf8;
    }
    
    /* لون رسالة الطالب (رمادي داكن أنيق) */
    .user .bubble { 
        background-color: #1e293b !important; 
        border: 1px solid #334155 !important;
        border-bottom-right-radius: 4px; 
    }
    
    div[data-testid="stTextInput"] input { background-color: #111827 !important; color: white !important; border: 1px solid #374151 !important; border-radius: 10px !important; }
    
    /* تحسين مظهر بطاقات الغيابات السريعة */
    div[data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        text-align: center !important;
    }
    div[data-testid="stMetricLabel"] { color: #9ca3af !important; font-size: 14px !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
</style>
""",
    unsafe_allow_html=True,
)

# 2. إعدادات جلب المفتاح السري لـ Gemini
if "GEMINI_API_KEY" in st.secrets:
  client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
  st.error("يرجى ضبط مفتاح الـ API في إعدادات الأسرار.")
  st.stop()

# 3. إعدادات روابط Google Sheets وجلب البيانات
SHEET_ID = "1Z1snF8YttXoUu1TA35jD8cfbKtX4uZYK2-h2kOVDSTk"
BASE_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
)


@st.cache_data(ttl=5)
def load_all_academic_data():
  default_subjects_info = {
      "math_eng": {
          "subject_name": "رياضيات هندسية",
          "professor": "لم يحدد بعد",
          "lecture_url": "غير متوفر حالياً",
      },
      "group_theory": {
          "subject_name": "جبر الزمر",
          "professor": "لم يحدد بعد",
          "lecture_url": "غير متوفر حالياً",
      },
      "fuzzy_math": {
          "subject_name": "رياضيات ضبابية",
          "professor": "لم يحدد بعد",
          "lecture_url": "غير متوفر حالياً",
      },
      "arabic": {
          "subject_name": "اللغة العربية",
          "professor": "لم يحدد بعد",
          "lecture_url": "غير متوفر حالياً",
      },
      "ai": {
          "subject_name": "الذكاء الاصطناعي",
          "professor": "لم يحدد بعد",
          "lecture_url": "غير متوفر حالياً",
      },
      "operations_res": {
          "subject_name": "بحوث العمليات",
          "professor": "لم يحدد بعد",
          "lecture_url": "غير متوفر حالياً",
      },
  }

  # قراءة تبويب معلومات المواد (الأساتذة والملازم)
  try:
    encoded_info = urllib.parse.quote("معلومات_المواد")
    df_info = pd.read_csv(BASE_URL + encoded_info, dtype=str)
    df_info.columns = df_info.columns.str.strip()
    for _, row in df_info.iterrows():
      key = str(row.get("subject_key", "")).strip()
      if key in default_subjects_info:
        default_subjects_info[key]["subject_name"] = str(
            row.get("subject_name", default_subjects_info[key]["subject_name"])
        ).strip()
        default_subjects_info[key]["professor"] = str(
            row.get("professor", "لم يحدد")
        ).strip()
        default_subjects_info[key]["lecture_url"] = str(
            row.get("lecture_url", "غير متوفر")
        ).strip()
  except Exception:
    pass

  # قراءة حسابات الطلاب
  try:
    encoded_accounts = urllib.parse.quote("حسابات_الطلاب")
    final_df = pd.read_csv(BASE_URL + encoded_accounts, dtype=str)
    final_df.columns = final_df.columns.str.strip()
    if "username" in final_df.columns:
      final_df["username"] = final_df["username"].astype(str).str.strip()
  except Exception:
    return (
        pd.DataFrame([{
            "username": "111111",
            "password": "123",
            "student_name": "علي حكمت حسن",
        }]),
        default_subjects_info,
    )

  materials = [
      "math_eng",
      "group_theory",
      "fuzzy_math",
      "arabic",
      "ai",
      "operations_res",
  ]

  for mat in materials:
    try:
      encoded_name = urllib.parse.quote(mat)
      df
