import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحلل الذكي للوثب العالي", page_icon="🧠", layout="wide")
st.markdown("""
    <style>
    /* تعديل التصميم ليكون آمناً ولا يكسر واجهة البرنامج */
    .block-container {
        direction: rtl;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    p, h1, h2, h3, h4, h5, h6, span, label, div {
        text-align: right !important;
    }
    .stMetric { 
        background-color: #f8fafc; 
        padding: 15px; 
        border-radius: 8px; 
        border-right: 4px solid #10b981; 
    }
    </style>
""", unsafe_allow_html=True)
