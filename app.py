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
    ".stApp { background-color: #fff8f1 !important; background-image: radial-gradient(#fdba74 1px, transparent 1px), radial-gradient(#fdba74 1px, #fff8f1 1px) !important; background-size: 32px 32px !important; background-position: 0 0, 16px 16px !important; }"
    "header { visibility: hidden !important; }"
    ".chat-box { display: flex; flex-direction: column; gap: 15px; padding: 20px; background: transparent !important; }"
    ".msg-wrapper { display: flex; width: 100%; }"
    ".msg-wrapper.assistant { justify-content: flex-end; }"
    ".msg-wrapper.user { justify-content: flex-start; }"
    ".bubble { padding: 14px 18px; border-radius: 18px; font-size: 16px; max-width: 82%; line-height: 1.6; }"
    ".assistant .bubble { background: linear-gradient(135deg, #f59e0b 0%, #ea580c 60%, #c2410c 100%) !important; color: white !important; border-bottom-left-radius: 4px; box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25); }"
    ".assistant .bubble a { display: inline-block; margin-top: 6px; margin-bottom: 4px; padding: 6px 14px; background-color: #fff7ed; color: #c2410c !important; text-decoration: none; border-radius: 8px; font-weight: bold; border: 1px solid #fed7aa; }"
    ".user .bubble { background-color: #ffffff !important; color: #1f2937 !important; border: 1px solid #fed7aa !important; border-bottom-right-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }"
    "div[data-testid='stTextInput'] input { background-color: #ffffff !important; color: #1f2937 !important; border: 1px solid #fdba74 !important; border-radius: 10px !important; }"
    "div[data-testid='stMetric'] { background-color: rgba(255, 255, 255, 0.9) !important; border: 1px solid #fed7aa !important; padding: 15px !important; border-radius: 14px !important; text-align: center !important; box-shadow: 0 4px 10px rgba(234, 88, 12, 0.06); }"
    "div[data-testid='stMetricLabel'] { color: #7c2d12 !important; font-size: 14px !important; font-weight: bold !important; }"
    "div[data-testid='stMetricValue'] { color: #ea580c !important; font-size: 22px !important; font-weight: bold !important; }"
    "h1, h2, h3, h4, p, label { color: #431407 !important; }"
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
        fallback_df = pd.DataFrame([{"username": "111111", "password": "123", "student_name": "علي حكمت حسن"}])
        return fallback_df, default_subjects_info, df_schedule

    materials = ["math_eng", "group_theory", "fuzzy_math", "arabic", "ai", "operations_res"]

    for mat in materials:
        try:
            encoded_name = urllib.parse.quote(mat)
            df_mat = pd.read_csv(BASE_URL + encoded_name, dtype=str)
            df_mat.columns = df_mat.columns.str.strip()
            if "username" in df_mat.columns:
                df_mat["username"] = df_mat["username"].astype(str).str.strip()
            if "student_name" in df_mat.columns:
                df_mat = df_mat.drop(columns=["student_name"])
            final_df = pd.merge(final_df, df_mat, on="username", how="left", suffixes=("", f"_{mat}"))
        except Exception:
            continue

    return final_df, default_subjects_info, df_schedule


df_students, subjects_info, df_schedule = load_all_academic_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_row = None

if not st.session_state.logged_in:
    st.markdown(f"<div style='text-align: center;'>{logo_login_html}</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #f97316; margin-top: 0; margin-bottom: 4px;'>قسم الرياضيات يرحب بكم</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #fbbf24; margin-top: 0; margin-bottom: 12px;'>برنامج معلومات الطالب</h4>", unsafe_allow_html=True)

    input_user = st.text_input("Username:").strip()
    input_pass = st.text_input("Password:", type="password").strip()
    submit_button = st.button("Log in now", use_container_width=True)

    if submit_button or (input_user and input_pass):
        match = df_students[(df_students["username"] == input_user) & (df_students["password"] == input_pass)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.student_row = match.iloc[0].to_dict()
            st.rerun()
        elif submit_button:
            st.error("❌ بيانات الدخول غير صحيحة أو الجدول تحت التحديث.")

    st.stop()

current_student = st.session_state.student_row

header_html = (
    "<div style='text-align: center; background-color: rgba(32, 20, 14, 0.75); padding: 16px; border-radius: 16px; border: 1px solid #452718; margin-bottom: 15px; backdrop-filter: blur(6px);'>"
    f"{logo_header_html}"
    "<h3 style='color: #f97316; margin: 0;'>كلية علوم الحاسوب والرياضيات</h3>"
    "</div>"
)
st.markdown(header_html, unsafe_allow_html=True)

col_name, col_logout = st.columns([4, 1])
with col_name:
    st.markdown(f"<h3 style='color: white; margin:0;'>مرحباً بك: {current_student.get('student_name', 'طالبنا العزيز')} 👋</h3>", unsafe_allow_html=True)
with col_logout:
    if st.button("خروج 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.chat_history = None
        st.rerun()

st.markdown("---")
st.markdown("<h4 style='color: #f97316;'>📊 موقف غيابات المواد الحالي:</h4>", unsafe_allow_html=True)


def get_attendance_progress(val_str):
    try:
        absent_days = int(val_str)
    except Exception:
        absent_days = 0

    max_days = 7
    percentage = min(int((absent_days / max_days) * 100), 100)
    fraction = min(absent_days / max_days, 1.0)

    if absent_days >= 7:
        status_text = f"🔴 محظور/فصل ({percentage}%)"
    elif absent_days >= 5:
        status_text = f"🟠 تحذير ثانٍ ({percentage}%)"
    elif absent_days >= 3:
        status_text = f"🟡 إنذار أول ({percentage}%)"
    else:
        status_text = f"🟢 وضع آمن ({percentage}%)"

    return absent_days, fraction, status_text


subjects = [
    ("math_eng", "math_eng_attendance"),
    ("group_theory", "group_theory_attendance"),
    ("fuzzy_math", "fuzzy_math_attendance"),
    ("arabic", "arabic_attendance"),
    ("ai", "ai_attendance"),
    ("operations_res", "operations_res_attendance"),
]

for row in range(2):
    cols = st.columns(3)
    for col_idx in range(3):
        subj_idx = row * 3 + col_idx
        subj_key, att_key = subjects[subj_idx]

        info = subjects_info.get(subj_key, {})
        title = info.get("subject_name", subj_key)
        prof_name = info.get("professor", "غير محدد")

        raw_val = current_student.get(att_key, "0")
        days, progress_val, status = get_attendance_progress(raw_val)

        with cols[col_idx]:
            st.metric(label=title, value=f"{days} / 7 أيام")
            st.markdown(f"<p style='text-align: center; font-size: 13px; color: #fb923c; margin-top: -12px; margin-bottom: 6px;'>👨‍🏫 {prof_name}</p>", unsafe_allow_html=True)
            st.progress(progress_val)
            st.markdown(f"<p style='text-align: center; font-size: 12px; margin-top: -10px; color: #e2cfc4;'>{status}</p>", unsafe_allow_html=True)

if not df_schedule.empty:
    with st.expander("📅 عرض الجدول الأسبوعي للمحاضرات"):
        display_df = df_schedule.rename(columns={
            "day": "اليوم",
            "time": "الوقت",
            "subject_name": "المادة",
            "hall": "القاعة"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

rules_list = [
    "أنت المساعد الأكاديمي الافتراضي لـ كلية علوم الحاسوب والرياضيات (قسم الرياضيات) في مسار بولونيا. مطورك هو علي حكمت حسن.",
    "1. التفاعل الفردي: أجب بسلاسة وود عن درجات الطالب وغياباته وسعيه ومستواه الأكاديمي.",
    "2. نطاق الصلاحيات: المواد الست (الرياضيات الهندسية، جبر الزمر، الرياضيات الضبابية، اللغة العربية، الذكاء الاصطناعي، بحوث العمليات) من حيث الدرجات، السعي، الغيابات، أسماء التدريسيين، الكويزات، الواجبات، الجدول الأسبوعي، والملازم.",
    "3. الملازم والتدريسيين: استخدم قائمة معلومات_المواد لمعرفة اسم التدريسي (professor) وقائمة الملازم (lectures).",
    "إذا طلب الطالب ملازم مادة معينة، اعرض له جميع الملازم المتوفرة لتلك المادة، وضع رابط كل ملزمة بصيغة Markdown هكذا: [📥 اسم الملزمة](الرابط). وإذا كانت القائمة فارغة أخبره بلطف أن الملازم لم تُرفع بعد.",
    "4. الجدول الأسبوعي: استخدم قائمة الجدول_الاسبوعي للإجابة عن مواعيد المحاضرات والأيام والقاعات الدراسية.",
    "5. الغيابات: أعمدة attendance تمثل عدد أيام الغياب الفعلي. اذكر الرقم الصافي فقط دون شرح نظام بولونيا. (3 فأكثر إنذار أول، 5 تحذير ثانٍ، 7 فصل).",
    "6. خط أحمر: إذا طلب حل مسألة أو واجب أو تقرير أو شرح درس، اعتذر بلطف وأخبره أن مهمتك هي استعراض البيانات الأكاديمية والملزمات والجدول فقط.",
    "7. لا تذكر لقب أبو لينا أبداً واكتفِ بذكر اسم المطور علي حكمت حسن."
]
STRICT_ACADEMIC_RULES = "\n".join(rules_list)

if "chat_history" not in st.session_state or st.session_state.chat_history is None:
    student_name = current_student.get("student_name", "طالبنا العزيز")
    welcome_msg = f"أهلاً بك يا {student_name} في مساعد كلية علوم الحاسوب والرياضيات. كيف يمكنني مساعدتك اليوم؟"
    st.session_state.chat_history = [{"role": "assistant", "content": welcome_msg}]


def format_safe_message(text):
    escaped_text = html.escape(text).replace("\n", "<br>")
    return re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<br><a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        escaped_text,
    )


if isinstance(st.session_state.chat_history, list):
    chat_html = '<div class="chat-box">'
    for msg in st.session_state.chat_history:
        role_class = "user" if msg["role"] == "user" else "assistant"
        safe_content = format_safe_message(msg["content"])
        chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{safe_content}</div></div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

if user_query := st.chat_input("اسأل عن درجاتك، غياباتك، الجدول، التدريسيين أو الملازم..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    recent_messages = st.session_state.chat_history[-6:]
    conversation_context = ""
    for msg in recent_messages:
        role_label = "الطالب" if msg["role"] == "user" else "المساعد"
        conversation_context += f"{role_label}: {msg['content']}\n"

    safe_student = {k: v for k, v in current_student.items() if k != "password"}

    schedule_records = df_schedule.to_dict(orient="records") if not df_schedule.empty else "غير متوفر حالياً"

    chat_prompt = (
        f"{STRICT_ACADEMIC_RULES}\n\n"
        f"معلومات المواد والملازم:\n{str(subjects_info)}\n\n"
        f"الجدول_الاسبوعي:\n{str(schedule_records)}\n\n"
        f"بيانات الطالب:\n{str(safe_student)}\n\n"
        f"المحادثة الأخيرة:\n{conversation_context}"
    )

    with st.spinner("🤖 جاري التفكير والكتابة..."):
        try:
            reply = client.models.generate_content(
                model="gemini-2.5-flash", contents=chat_prompt
            ).text
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
        except Exception as e:
            st.error(f"خطأ في الاتصال: {e}")
