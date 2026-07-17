import streamlit as st
from google import genai
import pandas as pd

st.set_page_config(page_title="مساعد جامعة الكوفة", page_icon="📊", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; }
    header { visibility: hidden !important; }
    .chat-box { display: flex; flex-direction: column; gap: 15px; padding: 20px; background-color: #000000 !important; }
    div[data-testid="stTextInput"] input { background-color: #1a1a1a !important; color: white !important; border: 1px solid #333 !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# إعدادات جلب المفتاح السري لـ Gemini
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("يرجى ضبط مفتاح الـ API in secrets.")
    st.stop()

SHEET_ID = "1Z1snF8YttXoUu1TA35jD8cfbKtX4uZYK2-h2kOVDSTk"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

@st.cache_data(ttl=5) # تحديث سريع جداً للفحص
def load_all_academic_data():
    # جلب الحسابات مباشرة بدون دمج في البداية لمعرفة أين الخلل
    df_accounts = pd.read_csv(BASE_URL + "حسابات_الطلاب", dtype=str)
    df_accounts.columns = df_accounts.columns.str.strip()
    for col in df_accounts.columns:
        df_accounts[col] = df_accounts[col].astype(str).str.strip()
    return df_accounts

# 🔍 شاشة الفحص الذكي لمعرفة المشكلة
st.warning("⚙️ وضع الفحص المطور نشط الآن:")
try:
    df_test = load_all_academic_data()
    st.success("✅ تم الاتصال بملف Google Sheet بنجاح! إليك البيانات التي يراها الكود حالياً:")
    st.dataframe(df_test) # عرض الجدول على الشاشة لترى الرموز والباسوردات الحية
except Exception as e:
    st.error(f"❌ فشل الكود في قراءة ملف Google Sheet. السبب: {e}")
    st.info("إذا ظهر هذا الخطأ، تأكد من أن اسم الورقة في الأسفل مكتوب 'حسابات_الطلاب' بالضبط وبدون أي مسافات زائدة.")

# نموذج تسجيل الدخول التجريبي
st.write("---")
input_user = st.text_input("Username (للتجربة):").strip()
input_pass = st.text_input("Password (للتجربة):", type="password").strip()

if st.button("تجرية المطابقة الحية"):
    if 'df_test' in locals():
        match = df_test[(df_test['username'] == input_user) & (df_test['password'] == input_pass)]
        if not match.empty:
            st.success(f"🎉 نجحت المطابقة! الحساب سليم للطالب: {match.iloc[0]['student_name']}")
        else:
            st.error("❌ لم تتطابق البيانات المكتوبة مع الجدول المعروض أعلاه.")
