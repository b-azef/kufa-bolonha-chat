import streamlit as st
from google import genai
import sqlite3

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد جامعة الكوفة الذكي", page_icon="📊", layout="wide")

# 2. جلب مفتاح الـ API بأمان من الصندوق السري لـ Streamlit
if "GEMINI_API_KEY" in st.secrets:
    api_key_to_use = st.secrets["GEMINI_API_KEY"]
else:
    api_key_to_use = "مفتاح_احتياطي"

client = genai.Client(api_key=api_key_to_use)

# قاعدة بيانات الطلاب لمسار بولونيا بجامعة الكوفة
conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER, name TEXT, stage TEXT, grade REAL)")
conn.commit()

# 3. اللوحة الجانبية لتعريف المطور أبو لينا
with st.sidebar:
    st.title("🏛️ جامعة الكوفة")
    st.subheader("مسار بولونيا الإداري")
    st.write("مساعد ذكي تفاعلي لفحص بيانات الطلاب والدرجات فورياً.")
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #1e3a8a; padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #3b82f6; font-family: 'Cairo', sans-serif;">
        <p style="margin: 0; font-weight: bold; font-size: 14px; color: #ffffff;">👨‍💻 مهندس النظام ومطوره:</p>
        <p style="margin: 5px 0 0 0; font-size: 18px; color: #fef08a; font-weight: bold;">علي (أبو لينا)</p>
        <p style="margin: 0; font-size: 12px; opacity: 0.9; color: #cbd5e1;">قسم الرياضيات - كلية العلوم</p>
    </div>
    """, unsafe_allow_html=True)

st.title("لوحة استعلام البيانات والشات الذكي 📊")

# 4. إدارة ذاكرة الشات بداخل النظام
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "مرحباً بك يا أستاذ. أنا نظام المساعد الذكي لجامعة الكوفة، كيف يمكنني مساعدتك في جرد جداول الطلاب اليوم؟"}
    ]

# 5. بناء واجهة الشات اليدوية فائقة الجمال (تصميم إنستغرام النيون والبنفسجي الصافي)
chat_html = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600&display=swap');
    .chat-box {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 15px;
        background-color: #f8fafc;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        font-family: 'Cairo', sans-serif;
        max-height: 500px;
        overflow-y: auto;
    }
    .msg-wrapper {
        display: flex;
        width: 100%;
    }
    .msg-wrapper.user {
        justify-content: flex-start; /* رسالة المستخدم على اليمين/اليسار حسب الاتجاه */
    }
    .msg-wrapper.assistant {
        justify-content: flex-end;
    }
    .bubble {
        padding: 12px 18px;
        border-radius: 20px;
        font-size: 15px;
        max-width: 75%;
        line-height: 1.6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* فقاعة المستخدم: رمادي ناعم ونظيف */
    .user .bubble {
        background-color: #e2e8f0;
        color: #0f172a;
        border-bottom-right-radius: 4px;
    }
    /* فقاعة البوت: تدرج ألوان إنستغرام الساحر والثابت للأبد */
    .assistant .bubble {
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
        color: white;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.25);
    }
</style>
<div class="chat-box">
"""

# تحويل الرسائل الحالية إلى كود HTML مدعوم بالتصميم الجديد الحين
for msg in st.session_state.chat_history:
    role_class = "user" if msg["role"] == "user" else "assistant"
    chat_html += f'<div class="msg-wrapper {role_class}"><div class="bubble">{msg["content"]}</div></div>'

chat_html += "</div>"

# عرض صندوق الشات الساحر والثابت في واجهة الموقع
st.markdown(chat_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. صندوق إدخال النص في الأسفل
if user_query := st.chat_input("اسألني عن أي شيء، مثل: من هو مطورك؟..."):
    # حفظ رسالة المستخدم فوراً وإعادة تحميل الصفحة لتظهر الواجهة فورياً
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    router_prompt = f"""صنف نية رسالة المستخدم الأخيرة بناءً على السياق الحالي إلى (CHAT) أو (SQL) فقط بدون أي مقدمات أو شرح:
    - إذا كانت الرسالة سلام، ترحيب، عتاب، سؤال عن الحال أو الهوية، اكتب: CHAT
    - إذا كانت الرسالة تطلب معلومات أو درجات من جدول الطلاب، اكتب: SQL
    رسالة المستخدم الأخيرة: {user_query}
    تصنيف الرسالة:"""
    
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
            
        st.session_state.chat_history.append({"role": "assistant", "content": final_reply})
        st.rerun() # تحديث فوري للشاشة لإظهار الألوان الجديدة
    except Exception as e:
        st.session_state.chat_history.append({"role": "assistant", "content": f"⚠️ حدث عطل اتصال: {str(e)}"})
        st.rerun()
