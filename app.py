import streamlit as st
import PyPDF2
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# ----------- LOAD MODEL -----------
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# ----------- STYLE -----------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #0f172a, #1e293b, #020617, #111827);
    background-size: 400% 400%;
    animation: gradient 10s ease infinite;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

h1, h2, h3 { color: #ffffff; }

.stButton>button {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-weight: bold;
}

.stTextArea textarea {
    background-color: #1e293b;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ----------- FUNCTIONS -----------

def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        content = page.extract_text()
        if content:  # ✅ FIX
            text += content
    return text.lower()

def extract_keywords(text):
    stopwords = {"a","an","the","and","or","for","with","to","of","in","on","at","by","is","are","was","were"}
    words = text.split()
    return set(
        word.lower().strip(".,-()[]{}")
        for word in words
        if word.lower() not in stopwords and len(word) > 2
    )

def calculate_score(resume_text, job_text):
    r = model.encode(resume_text, convert_to_tensor=True)
    j = model.encode(job_text, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(r, j)[0][0].item()
    score = ((similarity + 1) / 2) * 100

    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(job_text)

    matched = resume_words & job_words
    missing = job_words - resume_words

    return score, matched, missing

def generate_feedback(score, missing):
    missing = list(missing)  # ✅ FIX

    if score > 75:
        return "Excellent profile. Strong match for the role."
    elif score > 50:
        return f"Good profile. Improve: {', '.join(missing[:5])}" if missing else "Good profile."
    else:
        return f"Low match. Learn: {', '.join(missing[:5])}" if missing else "Low match."

def generate_report(name, score, matched, missing):
    matched = list(matched)   # ✅ FIX
    missing = list(missing)   # ✅ FIX

    report = f"""
===== AI RESUME SCREENING REPORT =====

Candidate Name: {name}
Match Score: {round(score,2)}%

------------------------------
✅ Matched Skills:
{', '.join(matched) if matched else 'None'}

------------------------------
⚠️ Missing Skills (GAPS):
{', '.join(missing) if missing else 'None'}

------------------------------
📌 Suggestions:
"""

    if missing:
        report += "\n- Learn missing skills listed above"
        report += "\n- Add projects using these skills"
        report += "\n- Optimize resume keywords"
    else:
        report += "\n- Strong profile, focus on advanced skills"

    report += "\n\n------------------------------\n🧠 AI Feedback:\n"

    if score > 75:
        report += "Excellent candidate"
    elif score > 50:
        report += "Good candidate with minor gaps"
    else:
        report += "Needs improvement"

    return report

# ----------- UI -----------

st.title("🚀 AI Resume Screener")
st.markdown("### ⚡ Hire Smarter. Faster. Better.")

st.sidebar.title("⚙️ Settings")

col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader("📄 Upload Resumes", type="pdf", accept_multiple_files=True)

with col2:
    job_description = st.text_area("📝 Job Description")

top_n = st.slider("🎯 Select Top Candidates", 1, 10, 3)

# ----------- MAIN -----------

if st.button("🔍 Analyze"):

    if uploaded_files and job_description:

        with st.spinner("Analyzing resumes... ⏳"):

            results = []

            for file in uploaded_files:
                text = extract_text_from_pdf(file)

                score, matched, missing = calculate_score(text, job_description)

                results.append({
                    "Name": file.name,
                    "Score": round(score, 2),
                    "Matched Skills": list(matched),
                    "Missing Skills": list(missing)
                })

            results.sort(key=lambda x: x["Score"], reverse=True)

        col1, col2 = st.columns(2)
        col1.metric("📄 Total Resumes", len(results))
        col2.metric("🏆 Top Score", f"{results[0]['Score']}%")

        st.markdown("## 🏆 Shortlisted Candidates")
        st.markdown("---")

        shortlisted = results[:top_n]

        for i, res in enumerate(shortlisted):

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                padding:15px;
                border-radius:10px;
                margin-bottom:10px;
            ">
                <b>⭐ Top {i+1}: {res['Name']}</b><br>
                Score: {res['Score']}%
            </div>
            """, unsafe_allow_html=True)

            if res["Score"] > 75:
                st.success("💼 Strong Hire Recommendation")
            elif res["Score"] > 50:
                st.info("🤝 Consider for Interview")
            else:
                st.warning("⚠️ Needs Review")

            st.success(f"✅ Matched: {', '.join(res['Matched Skills'])}")
            st.warning(f"⚠️ Missing: {', '.join(res['Missing Skills'])}")

            st.markdown("### 🧩 Skill Gap Analysis")
            if res["Missing Skills"]:
                st.error(", ".join(res["Missing Skills"]))
            else:
                st.success("No major gaps detected")

            st.markdown("### 💡 Suggestions")
            if res["Missing Skills"]:
                st.write("• Learn:", ", ".join(res["Missing Skills"][:5]))
                st.write("• Add projects using these skills")
                st.write("• Optimize resume keywords")
            else:
                st.write("• Focus on advanced skills")
                st.write("• Highlight achievements")

            feedback = generate_feedback(res["Score"], res["Missing Skills"])
            st.info(f"🧠 {feedback}")

            report = generate_report(
                res["Name"],
                res["Score"],
                res["Matched Skills"],
                res["Missing Skills"]
            )

            st.download_button(
                f"📄 Download Report - {res['Name']}",
                report,
                file_name=f"{res['Name']}_report.txt"
            )

            st.markdown("---")

        st.markdown("## 📋 All Candidates")

        for i, res in enumerate(results):
            st.markdown(f"**{i+1}. {res['Name']} — {res['Score']}%**")
            st.progress(int(res["Score"]))

        df = pd.DataFrame(results)
        st.download_button("📥 Download Results CSV", df.to_csv(index=False), "results.csv")

    else:
        st.warning("⚠️ Upload resumes and enter job description")