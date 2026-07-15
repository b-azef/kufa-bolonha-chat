import streamlit as st
from google import genai
import os

# 1. إعدادات المظهر المظلم الكامل والمستقر
st.set_page_config(page_title="مساعد جامعة الكوفة", page_icon="📊", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stSidebar"] { display: none !important; }
    header { visibility: hidden !important; }
    
    .chat-box {
        display: flex;
        flex-direction: column;
        gap: 15px;
        padding: 20px;
        background-color: #000000 !important;
        border: none !important;
    }
    
    .msg-wrapper.assistant { justify-content: flex-end; }
    .msg-wrapper.user { justify-content: flex-start; }
    
    .bubble {
        padding: 12px 18px;
        border-radius: 20px;
        font-size: 16px;
        max-width: 80%;
        color: white;
    }
    
    .assistant .bubble {
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%) !important;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.25);
    }
    
    .user .bubble {
        background-color: #262626 !important;
        border-bottom-right-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 2. إعدادات جلب المفتاح السري لـ Gemini
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("يرجى ضبط مفتاح الـ API في إعدادات الأسرار (Secrets).")
    st.stop()

# 3. قراءة بيانات الطلاب من الملف النصي students.txt
DATA_FILE = "students.txt"
students_info = ""

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            students_info = f.read()
    except Exception as e:
        students_info = f"خطأ أثناء قراءة الملف: {str(e)}"
else:
    students_info = "ملاحظة: ملف students.txt غير موجود في المستودع حالياً."

# إدارة ذاكرة الشات بداخل النظام
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "أهلاً بك يا أستاذ. أنا مساعد جامعة الكوفة الذكي، تم قراءة سجلات الطلاب النصية بنجاح ومستعد لتحليلها فورياً."}
    ]

# عرض الشات المظلم الفاخر
chat_html = '<div class="chat-box">'
for msg in st.session_state.chat_history:
    role_class = "user" if msg["role"] == "user" else "assistant"
    chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{msg["content"]}</div></div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# 4. محرك استقبال الأسئلة والرد الذكي
if user_query := st.chat_input("اسألني عن الطلاب (مثال: من هم الطلاب الراسبون في الرياضيات؟)..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # ضخ البيانات النصية مباشرة بداخل البرومبت ليفهمها جمناي
    chat_prompt = f"""أنت مساعد رقمي ذكي مخصص لجامعة الكوفة في مسار بولونيا الإداري. 
    مطورك وصانعك هو الطالب المبرمج الذكي علي (أبو لينا) من قسم الرياضيات بجامعة الكوفة.
    
    إليك قائمة ببيانات السجلات الحالية للطلاب:
    \"\"\"
    {students_info}
    \"\"\"
    
    بناءً على السجلات السابقة، أجب على سؤال المستخدم التالي بدقة واختصار شديد وبلغة عربية مفهومة ومنسقة:
    السؤال: {user_query}"""
    
    try:
        reply = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt).text
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"خطأ في الاتصال بالنموذج: {e}")
