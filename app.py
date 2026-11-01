import streamlit as st
from groq import Groq
import pypdf

st.set_page_config(page_title="JobPilot AI", page_icon="🤖", layout="wide")

st.title("🤖 JobPilot: AI Resume & Job Matcher")
st.write("Upload your resume, paste a target job description, and let Groq analyze your fit.")

# Retrieve API key securely from Streamlit secrets
groq_api_key = st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("Groq API Key not found! Please configure .streamlit/secrets.toml")
    st.stop()

client = Groq(api_key=groq_api_key)

# Layout: Two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 1. Upload Your Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    
    resume_text = ""
    if uploaded_file is not None:
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            resume_text += page.extract_text() or ""
        st.success(f"Resume loaded successfully ({len(resume_text)} characters extracted)!")

with col2:
    st.subheader("🎯 2. Target Job Description")
    job_description = st.text_area("Paste the Job Description here:", height=200)

st.markdown("---")

# Analysis Section
if st.button("🚀 Analyze Match & Tailor Resume", type="primary"):
    if not resume_text:
        st.warning("Please upload a resume first.")
    elif not job_description:
        st.warning("Please paste a job description.")
    else:
        with st.spinner("JobPilot AI is analyzing your fit..."):
            prompt = f"""
            You are an expert technical recruiter and career coach. 
            Analyze the candidate's resume against the target job description.

            RESUME:
            {resume_text}

            JOB DESCRIPTION:
            {job_description}

            Provide your response in the following structured format:
            1. **Match Score:** Give a percentage score (e.g., 85%) representing how well the resume fits the job.
            2. **Key Strengths:** Bullet points of what matches well.
            3. **Missing Skills / Keywords:** Important technical skills or requirements from the job description missing in the resume.
            4. **Tailoring Recommendations:** Actionable advice on how to rewrite resume bullet points to better target this role.
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional hiring manager and career mentor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            analysis_result = response.choices[0].message.content
            
            st.subheader("📊 AI Analysis & Feedback")
            st.markdown(analysis_result)
