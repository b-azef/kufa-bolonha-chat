import streamlit as st
from google import genai
import pandas as pd

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

# 3. جلب وتجميع البيانات من روابط Google Sheet
# 🚨 ضع الـ Sheet ID الخاص بملفك بين القوسين أدناه 🚨
SHEET_ID = "1Z1snF8YttXoUu1TA35jD8cfbKtX4uZYK2-h2kOVDSTk"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

@st.cache_data(ttl=60)
def load_all_academic_data():
    try:
        # جلب صفحة الحسابات الأساسية (التي تحتوي على الرمز والباسورد والاسم)
        df_accounts = pd.read_csv(BASE_URL + "حسابات_الطلاب")
        
        # جلب صفحات المواد المفصلة للأساتذة
        df_math = pd.read_csv(BASE_URL + "math")
        df_prog = pd.read_csv(BASE_URL + "prog")
        
        # حذف عمود اسم الطالب من صفحات المواد لتجنب تكرار الأعمدة عند الدمج البرمجي
        if 'student_name' in df_math.columns: df_math = df_math.drop(columns=['student_name'])
        if 'student_name' in df_prog.columns: df_prog = df_prog.drop(columns=['student_name'])
            
        # دمج الجداول بسلاسة في الخلفية بناءً على الرمز username
        final_df = pd.merge(df_accounts, df_math, on="username", how="left")
        final_df = pd.merge(final_df, df_prog, on="username", how="left")
        return final_df
    except:
        # بيانات احتياطية آمنة في حال لم يتم ربط الرابط الفعلي بشكل صحيح بعد
        return pd.DataFrame([
            {"username": "ali123", "password": "123", "student_name": "علي حكمت حسن", "math_attendance": 5, "prog_attendance": 2}
        ])

df_students = load_all_academic_data()

# 4. إدارة جلسة تسجيل الدخول (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_row = None

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: white;'>🏛️ بوابة مسار بولونيا - جامعة الكوفة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>سجل دخولك بنظام الفولدرات الموزعة للأساتذة</p>", unsafe_allow_html=True)
    
    input_user = st.text_input("اسم المستخدم (الرمز الكودي):")
    input_pass = st.text_input("كلمة المرور:", type="password")
    
    if st.button("تسجيل الدخول الآمن"):
        match = df_students[(df_students['username'].astype(str) == input_user) & (df_students['password'].astype(str) == input_pass)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.student_row = match.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("❌ بيانات الدخول غير صحيحة.")
    st.stop()

# --- بعد تسجيل الدخول بنجاح: واجهة النظام الخاصة بالطالب الحالية ---
current_student = st.session_state.student_row

st.markdown(f"<h3 style='color: white;'>مرحباً بك: {current_student['student_name']} 👋</h3>", unsafe_allow_html=True)

# 🚨 مستشعر فحص الغيابات التلقائي وإطلاق الإشعارات الملونة للـ الطالب
math_absences = 0
try:
    math_absences = int(current_student.get('math_attendance', 0))
except:
    math_absences = 0

if math_absences >= 7:
    st.error(f"⚠️ **تحذير نهائي (مادة الرياضيات):** لقد تجاوزت نسبة الغيابات المسموحة المحددة بـ ({math_absences} غيابات). أنت معرض للفصل النهائي بمسار بولونيا!")
elif math_absences >= 5:
    st.warning(f"🟠 **تحذير ثانٍ (مادة الرياضيات):** عدد غياباتك الحالي هو ({math_absences} غيابات). يرجى توخي الحذر والالتزام بالمحاضرات القادمة.")
elif math_absences >= 3:
    st.info(f"🟡 **إنذار أول (مادة الرياضيات):** تم تسجيل ({math_absences} غيابات) بحقك. يرجى مراجعة أستاذ المادة لتجنب تصاعد الإنذار.")

# زر تسجيل الخروج 🚪
if st.button("تسجيل الخروج 🚪"):
    st.session_state.logged_in = False
    st.session_state.chat_history = None
    st.rerun()

# إدارة وعرض الشات المظلم الفاخر
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "أنا مساعدك الأكاديمي المطور، تم سحب درجاتك وإشعاراتك حية من سجلات الكلية وجاهز للإجابة على أي استفسار يخص المواد السبعة."}
    ]

chat_html = '<div class="chat-box">'
for msg in st.session_state.chat_history:
    role_class = "user" if msg["role"] == "user" else "assistant"
    chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{msg["content"]}</div></div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# 5. محرك استقبال الأسئلة والرد الذكي من Gemini
if user_query := st.chat_input("اسألني عن أي درجة أو غياب في المواد..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # تلقين جمناي ببيانات هذا الطالب بخصوصية مطلقة
    chat_prompt = f"""أنت المساعد الأكاديمي لجامعة الكوفة لمسار بولونيا الإداري. مطورك هو المبرمج البارع علي (أبو لينا) من قسم الرياضيات.
    إليك ملف درجات الطالب الحالي المجمع تلقائياً:
    \"\"\"
    {str(current_student)}
    \"\"\"
    أجب على سؤال الطالب بدقة واختصار شديد وبلغة عربية مفهومة جداً ومنسقة: {user_query}"""
    
    try:
        reply = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt).text
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
