import re
import urllib.parse
from google import genai
import pandas as pd
import streamlit as st

# 1. إعدادات المظهر المظلم الكامل بثيم Maple
st.set_page_config(
    page_title="مساعد جامعة الكوفة - كلية علوم الحاسوب والرياضيات",
    page_icon="🏛️",
    layout="centered",
)

# 🎨 تخصيص الألوان (ثيم Maple الدافئ - برتقالي متدرج)
st.markdown(
    """
<style>
    .stApp { background-color: #0d0907 !important; }
    header { visibility: hidden !important; }
    .chat-box { display: flex; flex-direction: column; gap: 15px; padding: 20px; background-color: #0d0907 !important; }
    .msg-wrapper { display: flex; width: 100%; }
    .msg-wrapper.assistant { justify-content: flex-end; }
    .msg-wrapper.user { justify-content: flex-start; }
    .bubble { padding: 14px 18px; border-radius: 18px; font-size: 16px; max-width: 82%; color: white; line-height: 1.6; }
    
    /* لون رسالة المساعد (تدرج ثيم Maple: ذهبي عنبري -> برتقالي القيقب -> أحمر خريفي) */
    .assistant .bubble { 
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 50%, #b91c1c 100%) !important
