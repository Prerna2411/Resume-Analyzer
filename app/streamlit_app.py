import streamlit as st
import os
import tempfile
import fitz  # This is PyMuPDF
import re
from model import score_resume

from utils import compute_overlap, parse_experience

# --------- Utility to read text from uploaded file ----------
import fitz  # PyMuPDF
import streamlit as st

def read_file(file):
    text = ""
    if file.name.endswith(".pdf"):
        try:
            # Read from the uploaded file directly
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    else:
        st.warning("Unsupported file format. Please upload PDF or TXT files.")
    return text

# --------- Streamlit UI ----------
st.set_page_config(page_title="Resume Matcher", layout="centered")

st.title("📄 Resume Analyzer")

st.markdown("""
Upload a job description and one or more resumes.  
The system will rank resumes based on semantic similarity, keyword matching, and experience.
""")

# Upload JD
# Text Input for JD
st.subheader("📌 Enter or Upload Job Description")

jd_input_method = st.radio("Select Job Description Input Method", ["Type or Paste Text", "Upload PDF/TXT"])

jd_text = ""
jd_file = None

if jd_input_method == "Type or Paste Text":
    jd_text = st.text_area("✍️ Job Description Text", height=200)
else:
    jd_file = st.file_uploader("📂 Upload Job Description File", type=["pdf", "txt"])
    if jd_file:
        jd_text = read_file(jd_file)



# Upload Resumes
resumes = st.file_uploader("📂 Upload Resumes (PDF or TXT)", type=["pdf", "txt"], accept_multiple_files=True)

required_experience = st.number_input("Minimum Experience Required (years):", min_value=0, value=0)

# Run Matching
if st.button("🔍 Match Resumes"):
    if jd_text and resumes:
        jd_text = jd_text

        
        results = []
        for resume_file in resumes:
            resume_text = read_file(resume_file)
            result = score_resume(jd_text, resume_text, required_experience)
            result["filename"] = resume_file.name
            results.append(result)

        # Sort by final score
        results = sorted(results, key=lambda x: x["final_score"], reverse=True)

        st.success("✅ Matching Completed! See results below:")

        for idx, res in enumerate(results):
            st.markdown(f"### 📄 {res['filename']}")
            st.markdown(f"**✅ Final Score:** {res['final_score']} – {res['match_level']}  \n"
            f"**⭐ Rating:** {res['rating']}  \n"
            f"**Semantic Score:** {res['semantic_score']}  \n"
            f"**Keyword Score:** {res['keyword_score']}  \n"
            f"**Keyword Overlap:** {res['keyword_overlap']}  \n"
            f"**Experience:** {res.get('experience', 'N/A')} years")

        st.markdown(f"**🗝️ Matched Keywords:** `{', '.join(res['matched_keywords'])}`")
        if res['missing_keywords']:
            st.markdown(f"**❌ Missing Keywords:** `{', '.join(res['missing_keywords'])}`")

        st.markdown(f"**📝 Recommendation:** {res['recommendation']}")

        if res['suggestions']:
            st.markdown("**📈 Suggestions to Improve Match:**")
        for s in res['suggestions']:
            st.markdown(f"- {s}")

        st.markdown("---")

