import streamlit as st
from google import genai
import pandas as pd
import urllib.parse

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
    
    /* تحسين مظهر بطاقات الغيابات السريعة */
    div[data-testid="stMetric"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        text-align: center !important;
    }
    div[data-testid="stMetricLabel"] { color: #888888 !important; font-size: 14px !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# 2. إعدادات جلب المفتاح السري لـ Gemini
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("يرجى ضبط مفتاح الـ API في إعدادات الأسرار.")
    st.stop()

# 3. جلب وتجميع البيانات للمواد الـ 6 من روابط Google Sheet (تمت إضافة حماية الدمج هنا لمنع تداخل الأعمدة المتشابهة)
SHEET_ID = "1Z1snF8YttXoUu1TA35jD8cfbKtX4uZYK2-h2kOVDSTk"
BASE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

@st.cache_data(ttl=5)
def load_all_academic_data():
    try:
        encoded_accounts = urllib.parse.quote("حسابات_الطلاب")
        final_df = pd.read_csv(BASE_URL + encoded_accounts, dtype=str)
        final_df.columns = final_df.columns.str.strip()
        if 'username' in final_df.columns:
            final_df['username'] = final_df['username'].astype(str).str.strip()
    except Exception as e:
        return pd.DataFrame([{"username": "ali123", "password": "123", "student_name": "علي حكمت حسن"}])

    # قائمة المواد الست
    materials = ["math_eng", "group_theory", "fuzzy_math", "arabic", "ai", "operations_res"]
    
    for mat in materials:
        try:
            encoded_name = urllib.parse.quote(mat)
            df_mat = pd.read_csv(BASE_URL + encoded_name, dtype=str)
            df_mat.columns = df_mat.columns.str.strip()
            
            if 'username' in df_mat.columns:
                df_mat['username'] = df_mat['username'].astype(str).str.strip()
                
            if 'student_name' in df_mat.columns:
                df_mat = df_mat.drop(columns=['student_name'])
                
            # التعديل الحاسم: وضع لاحقة فارغة للمواد لمنع بايثون من تغيير أسماء الأعمدة الأصلية مثل الغيابات
            final_df = pd.merge(final_df, df_mat, on="username", how="left", suffixes=("", f"_{mat}"))
        except:
            continue
            
    return final_df

df_students = load_all_academic_data()

# 4. إدارة جلسة تسجيل الدخول (Session State)
# 4. إدارة جلسة تسجيل الدخول (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_row = None

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: white;'>🏛️ بوابة مسار بولونيا - جامعة الكوفة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Log in</p>", unsafe_allow_html=True)
    
    # مدخلات مباشرة لتسهيل التنقل والتفاعل السريع
    input_user = st.text_input("Username:").strip()
    
    # يظهر حقل الباسورد دائماً، وعند ادخال الرقم والضغط على Enter يتم الدخول فوراً
    input_pass = st.text_input("Password:", type="password").strip()
    
    submit_button = st.button("Log in now", use_container_width=True)
    
    # يتم التحقق سواء عند ضغط الزر أو عند الضغط على Enter بعد كتابة الباسورد
    if submit_button or (input_user and input_pass):
        match = df_students[(df_students['username'] == input_user) & (df_students['password'] == input_pass)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.student_row = match.iloc[0].to_dict()
            st.rerun()
        elif submit_button:
            st.error("❌ بيانات الدخول غير صحيحة أو الجدول تحت التحديث.")
            
    st.stop()
    

# --- بعد تسجيل الدخول بنجاح ---
current_student = st.session_state.student_row

col_name, col_logout = st.columns([4, 1])
with col_name:
    st.markdown(f"<h3 style='color: white; margin:0;'>مرحباً بك: {current_student.get('student_name', 'طالب جامعة الكوفة')} 👋</h3>", unsafe_allow_html=True)
with col_logout:
    if st.button("خروج 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.chat_history = None
        st.rerun()

st.markdown("---")

# 📊 قسم الملخص الأكاديمي السريع للغيابات للمواد الـ 6

    # 📊 قسم الملخص الأكاديمي السريع للغيابات للمواد الـ 6 مع شريط تقدم (Progress Bar)
st.markdown("<h4 style='color: #a855f7;'>📊 موقف غيابات المواد الحالي:</h4>", unsafe_allow_html=True)

# دالة مساعدة لحساب النسبة المئوية وتحديد الحالة البصرية
def get_attendance_progress(val_str):
    try:
        absent_days = int(val_str)
    except:
        absent_days = 0
    
    # الحد الأقصى للغياب بحسب مسار بولونيا هو 7 أيام (100%)
    max_days = 7
    percentage = min(int((absent_days / max_days) * 100), 100)
    fraction = min(absent_days / max_days, 1.0)
    
    # تحديد النص والرمز الحركي بناءً على عدد الأيام
    if absent_days >= 7:
        status_text = f"🔴 محظور/فصل ({percentage}%)"
    elif absent_days >= 5:
        status_text = f"🟠 تحذير ثانٍ ({percentage}%)"
    elif absent_days >= 3:
        status_text = f"🟡 إنذار أول ({percentage}%)"
    else:
        status_text = f"🟢 وضع آمن ({percentage}%)"
        
    return absent_days, fraction, status_text

# قائمة المواد مع عناوينها ومفاتيح البيانات الخاصة بها
subjects = [
    ("رياضيات هندسية", "math_eng_attendance"),
    ("جبر الزمر", "group_theory_attendance"),
    ("رياضيات ضبابية", "fuzzy_math_attendance"),
    ("اللغة العربية", "arabic_attendance"),
    ("الذكاء الاصطناعي", "ai_attendance"),
    ("بحوث العمليات", "operations_res_attendance")
]

# عرض المواد على شكل صفين (3 مواد في كل صف)
for row in range(2):
    cols = st.columns(3)
    for col_idx in range(3):
        subj_idx = row * 3 + col_idx
        title, key = subjects[subj_idx]
        raw_val = current_student.get(key, '0')
        days, progress_val, status = get_attendance_progress(raw_val)
        
        with cols[col_idx]:
            # عرض البطاقة الرقمية
            st.metric(label=title, value=f"{days} / 7 أيام")
            # شريط التقدم التفاعلي (Progress Bar)
            st.progress(progress_val)
            # نص الحالة والنسبة المئوية تحته مباشرة
            st.markdown(f"<p style='text-align: center; font-size: 12px; margin-top: -10px; color: #aaa;'>{status}</p>", unsafe_allow_html=True)

st.markdown("---")

# 🧠 القواعد الصارمة والمختصرة للغيابات والمهام الوظيفية لجمناي
STRICT_ACADEMIC_RULES = """
أنت المساعد الأكاديمي الافتراضي لجامعة الكوفة في مسار بولونيا. مطورك هو علي حكمت حسن من قسم الرياضيات.

التوجيهات والمهام الوظيفية المحددة لك:
1. التفاعل الفردي: عندما يسألك الطالب عن نفسه، درجاته، غياباته، أو مستواه الأكاديمي، أجب بسلاسة، ود، وطبيعية كاملة. قم بتحليل درجاته وسعيه الحالي لتشجيعه أو إعطائه نصيحة أكاديمية مفيدة بأسلوب مرن وراقٍ.
2. نطاق صلاحياتك الحصري: تخصصك هو عرض ومناقشة تفاصيل المواد الست (الرياضيات الهندسية، جبر الزمر، الرياضيات الضبابية، اللغة العربية، الذكاء الاصطناعي، وبحوث العمليات) من حيث: (الدرجات، السعي السنوي من 50، غيابات المواد، الكويزات، الواجبات البيئية homework، التبليغات الرسمية للقسم، جداول المحاضرات، ونظام الملازم الرقمية).

3. التعامل مع الغيابات (قاعدة صارمة):
   - أعمدة الـ `attendance` تمثل "عدد أيام الغياب الفعلي" للمادة المعنية.
   - عندما يسألك الطالب عن غيابه، اكتفِ فقط بذكر عدد أيام الغياب كـ رقم صافٍ بشكل طبيعي (مثال: "عدد أيام غيابك في الذكاء الاصطناعي هو 0 أيام"). لا تشرح قواعد مسار بولونيا ولا تقل "لا توجد درجات حضور في بولونيا".
   - إذا كان الرقم 3 أو أكثر في أي مادة، نبهه بوجود إنذار بحسب الأرقام التالية فقط: (الغيابات >= 3 إنذار أول 🟡، >= 5 تحذير ثانٍ 🟠، >= 7 تحذير نهائي وفصل 🔴).

4. خط أحمر صارم للمهام الخارجة عن وظيفتك: إذا طلب منك الطالب حل مسألة رياضية، كتابة تقرير، حل واجب، شرح درس، أو أي عمل دراسي نيابة عنه؛ يجب أن تتعذر منه فوراً وبأدب شديد وتخبره: 
"عذراً، هذا الأمر ليس من ضمن مهامي الوظيفية هنا. أنا مخصص لمساعدتك في استعراض سياقك الأكاديمي (الدرجات, الغيابات، الملازم، الجدول، والتبليغات) فقط لحساب مسار بولونيا. يمكنك الانتقال والذهاب إلى تطبيق أو نموذج ذكاء اصطناعي عام آخر ليساعدك في حل وشرح هذه المسائل."
5. إياك أن تذكر لقب "أبو لينا" في الشات نهائياً، واكتفِ بذكر الاسم المطور "علي حكمت حسن".
"""

# 5. الترحيب الأولي المنظم واللطيف
if "chat_history" not in st.session_state or st.session_state.chat_history is None:
    student_name = current_student.get('student_name', 'طالبنا العزيز')
    welcome_msg = f"أهلاً بك يا {student_name} في مساعد جامعة الكوفة الأكاديمي للمواد الست. أنا هنا لخدمتك ومساعدتك في تتبع درجاتك، غياباتك، التبليغات الرسمية، جداول المحاضرات، ونظام الملازم. كيف يمكنني مساعدتك أكاديمياً اليوم؟"
    st.session_state.chat_history = [{"role": "assistant", "content": welcome_msg}]

# 6. عرض الشات المظلم
if isinstance(st.session_state.chat_history, list):
    chat_html = '<div class="chat-box">'
    for msg in st.session_state.chat_history:
        role_class = "user" if msg["role"] == "user" else "assistant"
        chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{msg["content"]}</div></div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

# 7. استقبال الأسئلة اللاحقة وإخضاعها للمهام التنظيمية المحددة
if user_query := st.chat_input("Ask me..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    chat_prompt = f"""{STRICT_ACADEMIC_RULES}
    بيانات الطالب الحالي المخفية عن الشاشة: {str(current_student)}
    سؤال الطالب الحالي: {user_query}
    تذكر: اذكر الرقم الصافي للغيابات فوراً دون الدخول في تبريرات أو شرح للنظام البولوني الخارجي."""
    
    try:
        reply = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt).text
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
