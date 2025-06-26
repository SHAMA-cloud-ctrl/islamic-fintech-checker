import streamlit as st
import re
import json
from docx import Document
import fitz  # PyMuPDF

# إعداد الصفحة
st.set_page_config(page_title="تحليل شرعي للمنتج المالي", page_icon="🕌", layout="centered")

# تحميل قاعدة الفتاوى الشرعية
@st.cache_data
def load_fatwas():
    with open("fatwas.json", "r", encoding="utf-8") as f:
        return json.load(f)

fatwa_db = load_fatwas()

# دوال استخراج النص من الملفات
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        return "\n".join([page.get_text() for page in pdf])

# واجهة جذابة
st.markdown("""
<div style="text-align: center; padding: 10px; background-color: #f3f1e7; border-radius: 10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/AAOIFI-logo.png/600px-AAOIFI-logo.png" width="80">
    <h2 style="color: #2c3e50;">🕌 نظام تحليل توافق المنتجات المالية مع الشريعة</h2>
    <p style="color: #3e4b3c;">يدعم إدخال يدوي أو من ملفات PDF و Word - ويعرض المرجعية الشرعية لكل مخالفة</p>
</div>
""", unsafe_allow_html=True)

# تحميل الملف
uploaded_file = st.file_uploader("📎 قم برفع ملف المنتج (PDF أو Word)", type=["pdf", "docx"])
manual_input = st.text_area("✍️ أو أدخل وصف المنتج يدويًا هنا:", height=200)

# زر التحليل
if st.button("🔍 تحليل التوافق الشرعي"):
    full_text = ""

    # معالجة الملف
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            full_text += extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            full_text += extract_text_from_docx(uploaded_file)

    # إضافة الكتابة اليدوية
    if manual_input.strip():
        full_text += "\n" + manual_input.strip()

    # التحقق
    if not full_text.strip():
        st.warning("يرجى إدخال وصف أو رفع ملف.")
        st.stop()

    # تحليل النص
    results = []
    for item in fatwa_db:
        if re.search(item["keyword"], full_text, re.IGNORECASE):
            results.append(item)

    # عرض النتائج
    st.markdown("### 🧾 نتائج التحليل:")
    if results:
        st.error("❌ تم اكتشاف مخالفات شرعية:")
        for r in results:
            st.markdown(f"""
            <div style="border: 1px solid #d6d6d6; padding: 10px; border-radius: 8px; background-color: #fff8f0;">
                <strong>🔸 المخالفة:</strong> {r['keyword']}<br>
                <strong>📖 الشرح:</strong> {r['شرح']}<br>
                <strong>📚 المرجع:</strong> {r['المرجع']}<br>
                <strong>🧾 الفتوى:</strong> {r['الفتوى']}
            </div><br>
            """, unsafe_allow_html=True)
        st.info("⚖️ يُوصى بمراجعة هذا المنتج من طرف هيئة رقابة شرعية.")
    else:
        st.success("✅ لا توجد مخالفات شرعية ظاهرة.")
        st.markdown("🟢 يتوافق هذا المنتج – مبدئيًا – مع الضوابط الشرعية.")

