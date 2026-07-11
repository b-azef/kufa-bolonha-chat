import streamlit as st
from google import genai
import sqlite3

# 1. إعدادات المظهر المظلم الكامل
st.set_page_config(page_title="مساعد جامعة الكوفة", page_icon="📊", layout="centered")

st.markdown("""
<style>
    /* جعل كامل الصفحة سوداء */
    .stApp { background-color: #000000 !important; }
    
    /* إخفاء القائمة الجانبية والشعار العلوي والعناوين الكبيرة */
    [data-testid="stSidebar"] { display: none !important; }
    #لوحة-استعلام-البيانات-والشات-الذكي { display: none !important; }
    header { visibility: hidden !important; }
    
    /* تنسيق صندوق الشات ليكون متناغماً مع الخلفية السوداء */
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
    
    /* تدرج إنستغرام لرسائل البوت */
    .assistant .bubble {
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%) !important;
        border-bottom-left-radius: 4px;
    }
    
    /* رسالة المستخدم بلون رمادي داكن */
    .user .bubble {
        background-color: #262626 !important;
        border-bottom-right-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 2. إعدادات Gemini
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("يرجى ضبط مفتاح الـ API في الإعدادات.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "أهلاً بك. أنا مساعد جامعة الكوفة، كيف أخدمك اليوم؟"}]

# 3. عرض الشات
chat_html = '<div class="chat-box">'
for msg in st.session_state.chat_history:
    role_class = "user" if msg["role"] == "user" else "assistant"
    chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{msg["content"]}</div></div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# 4. الإدخال
if user_query := st.chat_input("اكتب رسالتك هنا..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    chat_prompt = f"""أنت مساعد جامعة الكوفة الذكي. صانعك هو المبرمج علي (أبو لينا). أجب بإيجاز.
    المستخدم: {user_query}"""
    
    try:
        reply = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt).text
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"خطأ: {e}")
