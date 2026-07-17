import streamlit as st
from google import genai
import pandas as pd
import urllib.parse  # 💡 المكتبة السحرية لحل مشكلة الحروف العربية

# 1. إعدادات المظهر المظلم الكامل والمستقر
st.set_page_config(page_title="مساعد جامعة الكوفة", page_icon="📊", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; }
    header { visibility: hidden !important; }
    .chat-box { display: flex; flex-direction: column; gap: 15px; padding: 20px; background-color: #000000 !important; }
    .msg-wrapper.assistant { justify-content: flex-end; }
    .msg-wrapper.user { justify-content: flex-start; }
    .bubble { padding: 12px 18px; border-radius: 20px; font-size: 16px; max-width: 80%; color: white; }
    .assistant .bubble { background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%) !important; border-bottom-left-radius: 4px; box-shadow: 0 4px 12px rgba(168, 85, 247, 0.25); }
    .user .bubble { background-color: #262626 !important; border-bottom-right-radius: 4px; }
    div[data-testid="stTextInput"] input { background-color: #1a1a1a !important; color: white !important; border: 1px solid #333 !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# 2. إعدادات جلب المفتاح السري لـ Gemini
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("يرجى ضبط مفتاح الـ API في إعدادات الأسرار.")
    st.stop()

# 3. جلب وتجميع البيانات من روابط Google Sheet باستخدام الـ ID الخاص بك
SHEET_ID = "1Z1snF8YttXoUu1TA35jD8cfbKtX4uZYK2-h2kOVDSTk"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

@st.cache_data(ttl=10)
def load_all_academic_data():
    try:
        # تشفير الكلمات العربية لتجنب خطأ ASCII المتسبب في التوقف
        sheet_accounts_encoded = urllib.parse.quote("حسابات_الطلاب")
        sheet_math_encoded = urllib.parse.quote("math")
        sheet_prog_encoded = urllib.parse.quote("prog")
        
        # قراءة البيانات بالنصوص النظيفة الصافية
        df_accounts = pd.read_csv(BASE_URL + sheet_accounts_encoded, dtype=str)
        df_math = pd.read_csv(BASE_URL + sheet_math_encoded, dtype=str)
        df_prog = pd.read_csv(BASE_URL + sheet_prog_encoded, dtype=str)
        
        # تنظيف الفراغات المخفية من أسماء الأعمدة والقيم
        for df in [df_accounts, df_math, df_prog]:
            df.columns = df.columns.str.strip()
            if 'username' in df.columns:
                df['username'] = df['username'].astype(str).str.strip()
        
        # حذف الأعمدة المكررة للأسماء من صفحات المواد لمنع تداخل الأعمدة
        if 'student_name' in df_math.columns: df_math = df_math.drop(columns=['student_name'])
        if 'student_name' in df_prog.columns: df_prog = df_prog.drop(columns=['student_name'])
            
        # دمج سحابي نظيف ومضمون بناءً على الرمز الأكاديمي الموحد
        final_df = pd.merge(df_accounts, df_math, on="username", how="left")
        final_df = pd.merge(final_df, df_prog, on="username", how="left")
        return final_df
    except Exception as e:
        # بيانات احتياطية آمنة جداً تمنع توقف التطبيق بالكامل
        return pd.DataFrame([
            {"username": "ali123", "password": "123", "student_name": "علي حكمت حسن", "math_attendance": "3", "prog_attendance": "4"}
        ])

df_students = load_all_academic_data()

# 4. إدارة جلسة تسجيل الدخول (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_row = None

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: white;'>🏛️ بوابة مسار بولونيا - جامعة الكوفة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Log in</p>", unsafe_allow_html=True)
    
    # نموذج متكامل يدعم الـ Enter بالكيبورد الخارجي
    with st.form("login_form", clear_on_submit=False):
        input_user = st.text_input("Username:").strip()
        input_pass = st.text_input("Password:", type="password").strip()
        
        submit_button = st.form_submit_button("Log in now", use_container_width=True)
        
        if submit_button:
            match = df_students[(df_students['username'] == input_user) & (df_students['password'] == input_pass)]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.student_row = match.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("❌ بيانات الدخول غير صحيحة. يرجى التأكد من الرمز السري.")
    st.stop()

# --- بعد تسجيل الدخول بنجاح ---
current_student = st.session_state.student_row
st.markdown(f"<h3 style='color: white;'>مرحباً بك: {current_student.get('student_name', 'طالب جامعة الكوفة')} 👋</h3>", unsafe_allow_html=True)

if st.button("تسجيل الخروج 🚪"):
    st.session_state.logged_in = False
    st.session_state.chat_history = None
    st.rerun()

# 5. مستشعر فحص الغيابات الشامل عبر Gemini لجميع المواد السبعة فور الدخول
if "chat_history" not in st.session_state:
    with st.spinner("جاري قيام المساعد بفحص سجل غياباتك في جميع المواد..."):
        init_prompt = f"""أنت المساعد الأكاديمي لجامعة الكوفة في مسار بولونيا. صانعك هو المبرمج البارع علي (أبو لينا) من قسم الرياضيات.
        إليك ملف درجات وغيابات الطالب الحالي بالكامل من جداول الأساتذة:
        \"\"\"
        {str(current_student)}
        \"\"\"
        قم بتحليل غيابات الطالب في جميع المواد الموجودة في ملفه فوراً (مثل math_attendance و prog_attendance وغيرها)، واكتب له رسالة ترحيبية أولى ذكية تحتوي تلقائياً على إنذارات الغياب حسب هذه القواعد الصارمة:
        - إذا كان الغياب في أي مادة يساوى أو أكبر من 3: قل له (إنذار أول 🟡) في مادة كذا.
        - إذا كان الغياب في أي مادة يساوى أو أكبر من 5: قل له (تحذير ثانٍ 🟠) في مادة كذا.
        - إذا كان الغياب في أي مادة يساوى أو أكبر من 7: قل له (تحذير نهائي وفصل 🔴) في مادة كذا.
        اكتب الرد بأسلوب تربوي منسق جداً ومحفز، واذكر له إنذاراته بوضوح كـ نقاط إيموجي ملونة في أول الرسالة ليراها فوراً."""
        
        try:
            first_reply = client.models.generate_content(model='gemini-2.5-flash', contents=init_prompt).text
            st.session_state.chat_history = [{"role": "assistant", "content": first_reply}]
        except:
            st.session_state.chat_history = [{"role": "assistant", "content": "أهلاً بك. أنا مساعدك الأكاديمي المطور، جاهز للمساعدة."}]

# عرض الشات المظلم
chat_html = '<div class="chat-box">'
for msg in st.session_state.chat_history:
    role_class = "user" if msg["role"] == "user" else "assistant"
    chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{msg["content"]}</div></div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

if user_query := st.chat_input("اسألني عن أي درجة أو غياب في المواد..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    chat_prompt = f"أنت المساعد الأكاديمي لجامعة الكوفة. بيانات الطالب: {str(current_student)}\nالسؤال: {user_query}"
    try:
        reply = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt).text
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
