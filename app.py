from dotenv import load_dotenv
import os
import time
import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import re

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini model options
model_options = {
    "Gemini 2.0 Flash (Next-Gen Fast & Smart)": "gemini-2.0-flash",
    "Gemini 2.0 Flash-Lite (Low Latency)": "gemini-2.0-flash-lite",
    "Gemini 1.5 Flash (Fast & Versatile)": "gemini-1.5-flash",
    "Gemini 1.5 Flash-8B (High Volume)": "gemini-1.5-flash-8b",
    "Gemini 1.5 Pro (Advanced Reasoning)": "gemini-1.5-pro"
}

# Prompts
PROMPTS = {
    "submit1": """
        You are an experienced Technical Human Resource Manager. Your task is to review the provided resume 
        against the job description. Highlight strengths and weaknesses in relation to the role.
    """,
    "submit2": """
    You are a Technical HR Manager with experience in assessing skill development. Evaluate the resume against the job description.

    Provide:
    1. Skills that are relevant and strong.
    2. Skills that are lacking or could be improved.
    3. Specific suggestions to enhance the candidate’s technical and soft skills for this role.
    """,
    "submit3": """
        You are an ATS scanner with HR experience. Evaluate resume vs. job description, list missing keywords, 
        and suggest skill improvements.
    """,
    "submit4": """
    You are an intelligent ATS (Applicant Tracking System) scanner. Analyze the resume against the job description and provide the following:

    1. An estimated **match percentage** between the resume and the job description.
    2. A brief explanation of how this score was determined — highlight key strengths and gaps.
    3. Keep your response short, structured, and easy to understand.
    """,
    "submit5": """
    You are a professional Technical Recruiter. Carefully review the candidate's resume and compare it with the job description.

    Provide:
    1. A judgment on whether this candidate is likely to be shortlisted for an interview (Yes, Maybe, or Unlikely).
    2. A brief explanation supporting your judgment based on relevant skills, experience, and alignment.
    3. Any critical gaps that might lower the chances.
    4. Suggestions to improve the chances of getting noticed or selected.
    """
}

# Streamlit UI
st.set_page_config(page_title="Resume Expert")
st.header("JobFit Analyzer")
st.subheader("This app reviews your resume using Gemini AI")

# Model selector
selected_model_label = st.selectbox("Choose Gemini Model:", list(model_options.keys()), index=0)
model_choice = model_options[selected_model_label]

# Inputs
# Inputs
job_desc = st.text_area("Job Description:", height=400)
st.markdown("**Note:** Please enter a job description before uploading your resume.")
uploaded_file = st.file_uploader("Upload your Resume (PDF)...", type=["pdf"])

response_output = ""
response_time_taken = None

if uploaded_file:
    st.success("PDF Uploaded Successfully")

# Extract PDF text
def extract_pdf_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return " ".join(page.get_text() for page in doc)

# Gemini response
def get_gemini_response(prompt, pdf_content, job_desc):
    model = genai.GenerativeModel(model_choice)
    start = time.time()
    response = model.generate_content([prompt, pdf_content, job_desc])
    end = time.time()
    return response.text, end - start

# Response handler
def handle_response(prompt_key_or_custom):
    if not job_desc.strip():
        st.warning("Please enter a job description before submitting.")
        return "", None
    if uploaded_file is None:
        st.warning("Please upload a PDF file to proceed.")
        return "", None

    with st.spinner("Generating response..."):
        uploaded_file.seek(0)
        pdf_text = extract_pdf_text(uploaded_file)
        prompt = PROMPTS.get(prompt_key_or_custom, prompt_key_or_custom)
        response_text, duration = get_gemini_response(prompt, pdf_text, job_desc)
        
        if prompt_key_or_custom == "submit4":
            import re
            match = re.search(r"(\d{1,3})\s*%", response_text)
            percentage = int(match.group(1)) if match else None
            return (percentage, response_text), duration

        return response_text, duration

if st.button("Percentage match"):
    result, response_time_taken = handle_response("submit4")
    if isinstance(result, tuple):
        percentage, explanation = result
        st.subheader("Match Percentage:")
        st.metric("Resume vs Job Description", f"{percentage}%")
        st.progress(percentage / 100)
        st.markdown("**Why this score?**")
        st.write(explanation)
    else:
        st.error("Couldn't extract a valid percentage from the response.")
        
# Buttons with individual handling
if st.button("Tell Me About the Resume"):
    response_output, response_time_taken = handle_response("submit1")

if st.button("How Can I Improvise my Skills"):
    response_output, response_time_taken = handle_response("submit2")

if st.button("What are the Keywords That are Missing"):
    response_output, response_time_taken = handle_response("submit3")

if st.button("Am I Likely to Get an Interview?"):
    response_output, response_time_taken = handle_response("submit5")

# Custom query
custom_query = st.text_input("Ask a specific question about your resume:")
if st.button("Answer My Query") and custom_query:
    response_output, response_time_taken = handle_response(custom_query)

# Show response
if response_output and not isinstance(response_output, int):
    st.subheader("The Response is:")
    st.write(response_output)
    if response_time_taken:
        st.caption(f"Response time: {response_time_taken:.2f} seconds")

# Footer
st.markdown("---\n*Resume Expert - Making Job Applications Easier*", unsafe_allow_html=True)
st.markdown("**Disclaimer:** This application is for educational purposes only and does not guarantee job placement or success.")