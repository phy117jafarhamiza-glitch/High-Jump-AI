import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# إعدادات الصفحة
st.set_page_config(page_title="المحلل الذكي للوثب العالي", page_icon="🧠", layout="wide")

st.title("🧠 المحلل الذكي للوثب العالي (AI Coach)")
st.markdown("يستخدم هذا النظام شبكات عصبية عميقة لتحليل فيديو القفزة آلياً واكتشاف الأخطاء الميكانيكية.")
st.markdown("---")

# إعداد مفتاح الذكاء الاصطناعي API
api_key = st.text_input("🔑 أدخل مفتاح Google Gemini API الخاص بك هنا:", type="password")
if api_key:
    genai.configure(api_key=api_key)

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 بيانات اللاعب")
    gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
    height = st.number_input("الطول الكلي (سم):", min_value=140, max_value=240, value=185)
    weight = st.number_input("الوزن (كجم):", min_value=40, max_value=120, value=75)

with col2:
    st.header("🎥 رفع الفيديو للتحليل الآلي")
    uploaded_video = st.file_uploader("ارفع فيديو القفزة (يُفضل تصوير من الجانب أو زاوية واضحة)", type=["mp4", "mov", "avi"])
    if uploaded_video:
        st.video(uploaded_video)

st.markdown("---")
if st.button("🚀 بدء التحليل بالذكاء الاصطناعي", use_container_width=True):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح API في الخانة المخصصة بالأعلى أولاً.")
    elif not uploaded_video:
        st.error("⚠️ يرجى رفع مقطع فيديو للتحليل.")
    else:
        with st.spinner('🤖 يقوم الذكاء الاصطناعي الآن بمشاهدة الفيديو وتحليل الميكانيكا الحيوية... يرجى الانتظار (قد يستغرق دقيقة)'):
            video_path = None
            video_file = None
            try:
                # حفظ الفيديو مؤقتاً
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_vid:
                    temp_vid.write(uploaded_video.read())
                    video_path = temp_vid.name

                # رفع الفيديو لخوادم الذكاء الاصطناعي
                video_file = genai.upload_file(path=video_path)
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                prompt = f"""
                أنت خبير عالمي في التحليل البيوميكانيكي والتدريب الرياضي الاحترافي، متخصص في رياضة الوثب العالي.
                شاهد هذا الفيديو بتمعن للاعب يقوم بالوثب.
                معلومات اللاعب:
                - الجنس: {gender}
                - الطول: {height} سم
                - الوزن: {weight} كجم
                
                المطلوب منك:
                1. قم بتحليل مرحلة الاقتراب.
                2. قم بتحليل مرحلة الارتقاء.
                3. قم بتحليل مرحلة الطيران وتخطي العارضة.
                4. حدد الخطأ الميكانيكي الرئيسي.
                5. اكتب برنامجاً تصحيحياً دقيقاً يتضمن تمارين لمعالجة هذا الخطأ.
                
                اكتب التقرير باللغة العربية بأسلوب احترافي وعلمي.
                """

                # --- الكود الذكي لاختيار الموديل تلقائياً ---
                available_models = [m.name for m in genai.list_models()]
                best_model = "gemini-1.5-flash" # الخيار الافتراضي
                
                if "models/gemini-1.5-flash" in available_models:
                    best_model = "gemini-1.5-flash"
                elif "models/gemini-1.5-pro" in available_models:
                    best_model = "gemini-1.5-pro"
                elif len(available_models) > 0:
                    best_model = available_models[0].replace("models/", "")

                model = genai.GenerativeModel(model_name=best_model)
                response = model.generate_content([video_file, prompt])

                st.markdown("---")
                st.header("📊 تقرير الذكاء الاصطناعي")
                st.write(response.text)

            except Exception as e:
                if "404" in str(e):
                    # في حال استمر الخطأ، سيطبع لك البرنامج أسماء الموديلات المسموحة لمفتاحك لكي نعرف المشكلة بدقة
                    try:
                        allowed = [m.name for m in genai.list_models()]
                        st.error(f"⚠️ مفتاحك لا يدعم هذا الموديل. الموديلات المسموحة لمفتاحك هي: {allowed}")
                    except:
                        st.error("⚠️ حدث خطأ في التحقق من المفتاح.")
                else:
                    st.error(f"حدث خطأ أثناء التحليل: {e}")
            
            finally:
                # تنظيف الملفات للحفاظ على السيرفر
                if video_file:
                    try:
                        genai.delete_file(video_file.name)
                    except: pass
                if video_path and os.path.exists(video_path):
                    try:
                        os.remove(video_path)
                    except: pass
