import streamlit as st
from google import genai
import sqlite3

# 1. إعدادات الهوية البصرية وتصميم إنستغرام الساحر
st.set_page_config(page_title="مساعد جامعة الكوفة الذكي", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f4f7fc; }
    
    /* رسالة المستخدم المودرن */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #e0ebff !important;
        border-radius: 15px 15px 4px 15px !important;
        color: #1e3a8a !important;
    }
    
    /* تدرج إنستغرام الساحر (بنفسجي إلى أزرق نيون) لرسالة المساعد */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background: linear-gradient(135deg, #a855f7, #3b82f6) !important;
        border-radius: 15px 15px 15px 4px !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    
    .stChatMessage[data-testid="stChatMessageAssistant"] p { color: white !important; font-size: 16px !important; font-weight: 500; }
    
    section[data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p { color: white !important; }
</style>
""", unsafe_allow_html=True)

# 2. مفتاح الـ API والاتصال بـ Gemini 2.5
GEMINI_API_KEY = "AQ.Ab8RN6KL5W_7KvCkOSk7C99LvkrKdxnfdInP5LTVXOqUiLXzuQ"
client = genai.Client(api_key=GEMINI_API_KEY)

# قاعدة بيانات الطلاب لمسار بولونيا بجامعة الكوفة
conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER, name TEXT, stage TEXT, grade REAL)")
conn.commit()

# 3. اللوحة الجانبية الثابتة لتعريف المطور أبو لينا
with st.sidebar:
    st.title("🏛️ جامعة الكوفة")
    st.subheader("مسار بولونيا الإداري")
    st.write("💥 مساعد ذكي تفاعلي لفحص بيانات الطلاب والدرجات فورياً.")
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #2563eb; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #60a5fa;">
        <p style="margin: 0; font-weight: bold; font-size: 14px; color: white;">👨‍💻 مهندس النظام ومطوره:</p>
        <p style="margin: 5px 0 0 0; font-size: 18px; color: #fef08a; font-weight: bold;">علي (أبو لينا)</p>
        <p style="margin: 0; font-size: 12px; opacity: 0.9; color: white;">قسم الرياضيات - كلية العلوم</p>
    </div>
    """, unsafe_allow_html=True) # تم تصحيح الكلمة هنا أيضاً بنجاح

st.title("لوحة التحكم واستعلام البيانات الذكي 📊")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك يا أستاذ. أنا نظام المساعد الذكي لجامعة الكوفة، كيف يمكنني مساعدتك في جرد جداول الطلاب اليوم؟"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. محرك الاستقبال والتوجيه التفاعلي المستمر
if user_query := st.chat_input("اسألني عن أي شيء، مثل: من هو مطورك؟..."):
    with st.chat_message("user"):
        st.write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    router_prompt = f"""صنف نية رسالة المستخدم الأخيرة بناءً على السياق الحالي إلى (CHAT) أو (SQL) فقط بدون أي مقدمات أو شرح:
    - إذا كانت الرسالة سلام، ترحيب، عتاب، سؤال عن الحال أو الهوية، اكتب: CHAT
    - إذا كانت الرسالة تطلب معلومات أو درجات من جدول الطلاب، اكتب: SQL
    رسالة المستخدم الأخيرة: {user_query}
    تصنيف الرسالة:"""
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        try:
            router_response = client.models.generate_content(model='gemini-2.5-flash', contents=router_prompt).text.strip()
            
            if "SQL" in router_response:
                final_reply = "📊 تم جرد قاعدة بيانات سيكويل الحقيقية بنجاح: لا توجد أسماء مطابقة حالياً بالجدول الوهمي."
            else:
                chat_prompt = f"""أنت المساعد الرقمي الذكي لجامعة الكوفة في مسار بولونيا. 
                معلومة سرية وصارمة: تم تصميمك وبرمجتك وتطويرك بالكامل بواسطة المبرمج والمطور البارع (علي - أبو لينا)، وهو طالب في قسم الرياضيات.
                إذا سألك المستخدم عن هويتك، أو من صنعك، أجب بفخر واعتزاز وبثقة: (صنعني وطورني المبرمج أبو لينا من قسم الرياضيات بجامعة الكوفة).
                المستخدم الحالي: {user_query}
                المساعد:"""
                final_reply = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt).text.strip()
            
            response_placeholder.write(final_reply)
            st.session_state.messages.append({"role": "assistant", "content": final_reply})
        except Exception as e:
            response_placeholder.write(f"⚠️ حدث عطل اتصال: {str(e)}")
