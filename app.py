  import re
import urllib.parse
from google import genai
import pandas as pd
import streamlit as st

# 1. إعدادات المظهر المظلم الكامل والمستقر
st.set_page_config(
    page_title="مساعد جامعة الكوفة - كلية علوم الحاسوب والرياضيات",
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
    
    /* لون رسالة المساعد (أزرق أكاديمي متدرج) */
    .assistant .bubble { 
        background: linear-gradient(135deg, #1d4ed8 0%, #0ea5e9 100%) !important; 
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
      df_mat = pd.read_csv(BASE_URL + encoded_name, dtype=str)
      df_mat.columns = df_mat.columns.str.strip()

      if "username" in df_mat.columns:
        df_mat["username"] = df_mat["username"].astype(str).str.strip()

      if "student_name" in df_mat.columns:
        df_mat = df_mat.drop(columns=["student_name"])

      final_df = pd.merge(
          final_df, df_mat, on="username", how="left", suffixes=("", f"_{mat}")
      )
    except Exception:
      continue

  return final_df, default_subjects_info


df_students, subjects_info = load_all_academic_data()

# 4. إدارة جلسة تسجيل الدخول
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.student_row = None

if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center; color: white; margin-bottom: 5px;'>🏛️"
      " جامعة الكوفة</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h4 style='text-align: center; color: #38bdf8; margin-top: 0;'>كلية علوم"
      " الحاسوب والرياضيات - بوابة مسار بولونيا</h4>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #888;'>Log in</p>",
      unsafe_allow_html=True,
  )

  input_user = st.text_input("Username:").strip()
  input_pass = st.text_input("Password:", type="password").strip()
  submit_button = st.button("Log in now", use_container_width=True)

  if submit_button or (input_user and input_pass):
    match = df_students[
        (df_students["username"] == input_user)
        & (df_students["password"] == input_pass)
    ]
    if not match.empty:
      st.session_state.logged_in = True
      st.session_state.student_row = match.iloc[0].to_dict()
      st.rerun()
    elif submit_button:
      st.error("❌ بيانات الدخول غير صحيحة أو الجدول تحت التحديث.")

  st.stop()

# --- بعد تسجيل الدخول بنجاح ---
current_student = st.session_state.student_row

# ترويسة الكلية في الواجهة الرئيسية
st.markdown(
    """
<div style='text-align: center; background-color: #111827; padding: 12px; border-radius: 12px; border: 1px solid #1f2937; margin-bottom: 15px;'>
    <h4 style='color: #38bdf8; margin: 0;'>🏛️ جامعة الكوفة - كلية علوم الحاسوب والرياضيات</h4>
    <p style='color: #9ca3af; font-size: 13px; margin: 4px 0 0 0;'>قسم الرياضيات | المساعد الذكي لمسار بولونيا</p>
</div>
""",
    unsafe_allow_html=True,
)

col_name, col_logout = st.columns([4, 1])
with col_name:
  st.markdown(
      f"<h3 style='color: white; margin:0;'>مرحباً بك:"
      f" {current_student.get('student_name', 'طالب جامعة الكوفة')} 👋</h3>",
      unsafe_allow_html=True,
  )
with col_logout:
  if st.button("خروج 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.chat_history = None
    st.rerun()

st.markdown("---")

# 📊 قسم الملخص الأكاديمي السريع للغيابات مع اسم التدريسي
st.markdown(
    "<h4 style='color: #38bdf8;'>📊 موقف غيابات المواد الحالي:</h4>",
    unsafe_allow_html=True,
)


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
      st.markdown(
          "<p style='text-align: center; font-size: 13px; color: #38bdf8;"
          f" margin-top: -12px; margin-bottom: 6px;'>👨‍🏫 {prof_name}</p>",
          unsafe_allow_html=True,
      )
      st.progress(progress_val)
      st.markdown(
          "<p style='text-align: center; font-size: 12px; margin-top: -10px;"
          f" color: #aaa;'>{status}</p>",
          unsafe_allow_html=True,
      )

st.markdown("---")

# 🧠 التوجيهات والقواعد المحددة لـ Gemini
STRICT_ACADEMIC_RULES = """
أنت المساعد الأكاديمي الافتراضي لجامعة الكوفة - كلية علوم الحاسوب والرياضيات (قسم الرياضيات) في مسار بولونيا. مطورك هو علي حكمت حسن من قسم الرياضيات.

التوجيهات والمهام الوظيفية المحددة لك:
1. التفاعل الفردي: عندما يسألك الطالب عن نفسه، درجاته، غياباته، أو مستواه الأكاديمي، أجب بسلاسة، ود، وطبيعية كاملة. قم بتحليل درجاته وسعيه الحالي لتشجيعه أو إعطائه نصيحة أكاديمية مفيدة بأسلوب مرن وراقٍ.
2. نطاق صلاحياتك الحصري: تخصصك هو عرض ومناقشة تفاصيل المواد الست (الرياضيات الهندسية، جبر الزمر، الرياضيات الضبابية، اللغة العربية، الذكاء الاصطناعي، وبحوث العمليات) من حيث: (الدرجات، السعي السنوي من 50، غيابات المواد، أسماء التدريسيين، الكويزات، الواجبات homework، جداول المحاضرات، ونظام الملازم الرقمية).

3. الملازم وأسماء التدريسيين:
   - لديك في السياق أدناه قائمة `معلومات_المواد` وتحتوي على اسم التدريسي (`professor`) ورابط الملزمة (`lecture_url`) لكل مادة.
   - إذا سألك الطالب عن اسم أستاذ/تدريسي مادة معينة، أجب باسمه مباشرة من القائمة.
   - إذا طلب الطالب ملزمة أو محاضرات مادة معينة، أعطه رابط التحميل الخاص بها بصيغة Markdown هكذا: [📥 تحميل ملزمة المادة](الرابط). وإذا كان الرابط "غير متوفر حالياً"، أخبره بلطف أن الملزمة لم تُرفع بعد.

4. التعامل مع الغيابات:
   - أعمدة الـ `attendance` تمثل "عدد أيام الغياب الفعلي" للمادة المعنية.
   - عندما يسألك الطالب عن غيابه، اكتفِ فقط بذكر عدد أيام الغياب كـ رقم صافٍ بشكل طبيعي (مثال: "عدد أيام غيابك في الذكاء الاصطناعي هو 0 أيام"). لا تشرح قواعد مسار بولونيا.
   - إذا كان الرقم 3 أو أكثر في أي مادة، نبهه بوجود إنذار بحسب الأرقام التالية فقط: (الغيابات >= 3 إنذار أول 🟡، >= 5 تحذير ثانٍ 🟠، >= 7 تحذير نهائي وفصل 🔴).

5. خط أحمر صارم للمهام الخارجة عن وظيفتك: إذا طلب منك الطالب حل مسألة رياضية، كتابة تقرير، حل واجب، شرح درس، أو أي عمل دراسي نيابة عنه؛ يجب أن تتعذر منه فوراً وبأدب شديد وتخبره: 
"عذراً، هذا الأمر ليس من ضمن مهامي الوظيفية هنا. أنا مخصص لمساعدتك في استعراض سياقك الأكاديمي (الدرجات، الغيابات، الملازم، والجدول) فقط لحساب مسار بولونيا. يمكنك الانتقال والذهاب إلى تطبيق أو نموذج ذكاء اصطناعي عام آخر ليساعدك في حل وشرح هذه المسائل."
6. إياك أن تذكر لقب "أبو لينا" في الشات نهائياً، واكتفِ بذكر الاسم المطور "علي حكمت حسن".
"""

# 5. الترحيب الأولي
if "chat_history" not in st.session_state or st.session_state.chat_history is None:
  student_name = current_student.get("student_name", "طالبنا العزيز")
  welcome_msg = (
      f"أهلاً بك يا {student_name} في مساعد كلية علوم الحاسوب والرياضيات -"
      " جامعة الكوفة. أنا هنا لمساعدتك في تتبع درجاتك، غياباتك، أسماء"
      " التدريسيين، وتحميل الملازم. كيف يمكنني مساعدتك اليوم؟"
  )
  st.session_state.chat_history = [{"role": "assistant", "content": welcome_msg}]


# دالة مساعدة لتحويل روابط Markdown إلى أزرار HTML قابلة للنقر داخل فقاعات الشات
def format_links_to_html(text):
  return re.sub(
      r"\[([^\]]+)\]\((https?://[^\)]+)\)",
      r'<br><a href="\2" target="_blank">\1</a>',
      text,
  )


# 6. عرض الشات
if isinstance(st.session_state.chat_history, list):
  chat_html = '<div class="chat-box">'
  for msg in st.session_state.chat_history:
    role_class = "user" if msg["role"] == "user" else "assistant"
    formatted_content = format_links_to_html(msg["content"])
    chat_html += (
        f'<div class="msg-wrapper {role_class}"><div'
        f' class="bubble">{formatted_content}</div></div>'
    )
  chat_html += "</div>"
  st.markdown(chat_html, unsafe_allow_html=True)

# 7. استقبال أسئلة الطالب وتمرير السياق لنموذج Gemini
if user_query := st.chat_input("اسأل عن درجاتك، غياباتك، التدريسيين أو الملازم..."):
  st.session_state.chat_history.append({"role": "user", "content": user_query})

  conversation_context = ""
  for msg in st.session_state.chat_history:
    role_label = "الطالب" if msg["role"] == "user" else "المساعد"
    conversation_context += f"{role_label}: {msg['content']}\n"

  chat_prompt = f"""{STRICT_ACADEMIC_RULES}

    معلومات المواد (التدريسيين وروابط الملازم):
    {str(subjects_info)}

    بيانات الطالب الحالي المخفية عن الشاشة:
    {str(current_student)}

    سجل المحادثة الكامل حتى الآن:
    {conversation_context}

    تذكر: أجب بناءً على سياق المحادثة أعلاه واذكر الأرقام الصافية للغيابات دون شرح للنظام البولوني."""

  with st.spinner("🤖 جاري التفكير والكتابة..."):
    try:
      reply = client.models.generate_content(
          model="gemini-2.5-flash", contents=chat_prompt
      ).text
      st.session_state.chat_history.append(
          {"role": "assistant", "content": reply}
      )
      st.rerun()
    except Exception as e:
      st.error(f"خطأ في الاتصال: {e}")
