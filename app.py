import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحلل الذكي للوثب العالي", page_icon="🧠", layout="wide")
st.markdown("""
    <style>
    * { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 8px; border-right: 4px solid #10b981; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 المحلل الذكي للوثب العالي (AI Coach)")
st.markdown("يستخدم هذا النظام شبكات عصبية عميقة لتحليل فيديو القفزة آلياً واكتشاف الأخطاء الميكانيكية.")
st.markdown("---")

# 2. إعداد مفتاح الذكاء الاصطناعي API (اطلب من المستخدم إدخاله)
api_key = st.sidebar.text_input("🔑 أدخل مفتاح Google Gemini API الخاص بك:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. واجهة إدخال بيانات اللاعب ورفع الفيديو
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 بيانات اللاعب")
    gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
    height = st.number_input("الطول الكلي (سم):", min_value=140, max_value=240, value=185)
    weight = st.number_input("الوزن (كجم):", min_value=40, max_value=120, value=75)
    
    com_multiplier = 0.565 if gender == "ذكر" else 0.545
    com = round(height * com_multiplier, 1)

with col2:
    st.header("🎥 رفع الفيديو للتحليل الآلي")
    uploaded_video = st.file_uploader("ارفع فيديو القفزة (يُفضل تصوير من الجانب أو زاوية واضحة)", type=["mp4", "mov"])
    if uploaded_video:
        st.video(uploaded_video)

# 4. زر التحليل بالذكاء الاصطناعي
if st.button("🚀 بدء التحليل بالذكاء الاصطناعي", use_container_width=True):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح API في القائمة الجانبية أولاً لتفعيل الذكاء الاصطناعي.")
    elif not uploaded_video:
        st.error("⚠️ يرجى رفع مقطع فيديو للتحليل.")
    else:
        with st.spinner('🤖 يقوم الذكاء الاصطناعي الآن بمشاهدة الفيديو وتحليل الميكانيكا الحيوية... يرجى الانتظار (قد يستغرق دقيقة)'):
            try:
                # حفظ الفيديو في ملف مؤقت ليتمكن الذكاء الاصطناعي من قراءته
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_vid:
                    temp_vid.write(uploaded_video.read())
                    video_path = temp_vid.name

                # رفع الفيديو إلى خوادم Gemini
                video_file = genai.upload_file(path=video_path)
                
                # الانتظار حتى يتم معالجة الفيديو في الخادم
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                # إعداد التوجيه الدقيق (Prompt) للذكاء الاصطناعي
                prompt = f"""
                أنت خبير عالمي في التحليل البيوميكانيكي والتدريب الرياضي الاحترافي، متخصص في رياضة الوثب العالي (طريقة الفوسفري فلوب).
                شاهد هذا الفيديو بتمعن للاعب يقوم بالوثب.
                معلومات اللاعب:
                - الجنس: {gender}
                - الطول: {height} سم (مركز الثقل التقريبي يقع عند {com} سم)
                - الوزن: {weight} كجم
                
                المطلوب منك:
                1. قم بتحليل مرحلة الاقتراب (هل القوس سليم؟ هل هناك فقدان للسرعة؟).
                2. قم بتحليل مرحلة الارتقاء (زاوية غرس القدم، حركة الذراعين والركبة الحرة).
                3. قم بتحليل مرحلة الطيران وتخطي العارضة (توقيت التقوس، سحب الساقين).
                4. حدد الخطأ الميكانيكي الرئيسي الذي تسبب في فشل المحاولة (أو الذي يمكن تحسينه).
                5. اكتب برنامجاً تصحيحياً دقيقاً يتضمن تمرينين أو ثلاثة لمعالجة هذا الخطأ.
                
                اكتب التقرير باللغة العربية بأسلوب احترافي وعلمي ومنسق بشكل جميل.
                """

                # استدعاء النموذج (Gemini 1.5 Pro هو الأفضل للفيديو)
                model = genai.GenerativeModel(model_name="gemini-1.5-pro")
                response = model.generate_content([video_file, prompt])

                # عرض النتائج
                st.markdown("---")
                st.header("📊 تقرير الذكاء الاصطناعي")
                st.write(response.text)

                # مسح الملف من الخادم بعد الانتهاء للحفاظ على الخصوصية
                genai.delete_file(video_file.name)
                os.remove(video_path)

            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
