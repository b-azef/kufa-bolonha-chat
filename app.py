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
    ".stApp { background: radial-gradient(circle at top, #2c1810 0%, #160e0a 55%, #0e0907 100%) !important; }"
    "header { visibility: hidden !important; }"
    ".chat-
