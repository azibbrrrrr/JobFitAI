from dotenv import load_dotenv
import os
import time
import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import re
from datetime import datetime

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Page configuration with custom theme
st.set_page_config(
    page_title="JobFit Analyzer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: white;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #F3F4F6;
        margin-bottom: 1rem;
    }
    .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.3rem;
        padding: 0.5rem;
        color: white;
        font-weight: 500;
    }
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
        text-align: center;
        color: #6B7280;
    }
    .result-card {
        background-color: #F9FAFB;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563EB;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Gemini model options with descriptions
model_options = {
    "Gemini 2.0 Flash (Next-Gen Fast & Smart)": "gemini-2.0-flash",
    "Gemini 2.0 Flash-Lite (Low Latency)": "gemini-2.0-flash-lite", 
    "Gemini 1.5 Flash (Fast & Versatile)": "gemini-1.5-flash",
    "Gemini 1.5 Flash-8B (High Volume)": "gemini-1.5-flash-8b",
    "Gemini 1.5 Pro (Advanced Reasoning)": "gemini-1.5-pro"
}

# Prompts dictionary
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
    3. Specific suggestions to enhance the candidate's technical and soft skills for this role.
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

def extract_pdf_text(uploaded_file):
    """Extract text from PDF file"""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return " ".join(page.get_text() for page in doc)

def get_gemini_response(prompt, pdf_content, job_desc):
    """Get response from Gemini model"""
    model = genai.GenerativeModel(model_choice)
    start = time.time()
    response = model.generate_content([prompt, pdf_content, job_desc])
    end = time.time()
    return response.text, end - start

def validate_inputs():
    """Validate that both job description and resume are provided"""
    if not job_desc.strip():
        st.error("⚠️ Please enter a job description before submitting.")
        return False
    if uploaded_file is None:
        st.error("⚠️ Please upload a PDF resume to proceed.")
        return False
    return True

def handle_response(prompt_key_or_custom):
    """Handle response generation with error handling"""
    if not validate_inputs():
        return "", None

    with st.spinner("Analyzing your resume... This may take a moment"):
        try:
            uploaded_file.seek(0)
            pdf_text = extract_pdf_text(uploaded_file)
            prompt = PROMPTS.get(prompt_key_or_custom, prompt_key_or_custom)
            response_text, duration = get_gemini_response(prompt, pdf_text, job_desc)
            
            if prompt_key_or_custom == "submit4":
                match = re.search(r"(\d{1,3})\s*%", response_text)
                percentage = int(match.group(1)) if match else None
                return (percentage, response_text), duration

            return response_text, duration
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return f"Error: {str(e)}", None

def display_response(response_output, response_time_taken=None):
    """Display formatted response"""
    if response_output and not isinstance(response_output, tuple) and not isinstance(response_output, int):
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Analysis Results:</h3>", unsafe_allow_html=True)
        st.write(response_output)
        if response_time_taken:
            st.caption(f"⏱️ Response time: {response_time_taken:.2f} seconds")
        st.markdown("</div>", unsafe_allow_html=True)

def save_response_history(response, query_type):
    """Save response to session state history"""
    if 'response_history' not in st.session_state:
        st.session_state.response_history = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.response_history.append({
        "type": query_type,
        "timestamp": timestamp,
        "response": response
    })

# Initialize session state for inputs status
if 'inputs_ready' not in st.session_state:
    st.session_state.inputs_ready = False

# Main app layout
st.markdown("<h1 class='main-header'>JobFit Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Optimize your job application with AI-powered resume analysis</p>", unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<div class='section-header'>Upload Information</div>", unsafe_allow_html=True)
    
    job_desc = st.text_area(
        "📋 Job Description:", 
        placeholder="Paste the job description here...",
        height=250
    )
    
    with st.expander("📝 Resume Upload"):
        uploaded_file = st.file_uploader(
            "Upload your Resume (PDF format only)", 
            type=["pdf"],
            help="Your resume will be analyzed against the job description"
        )
        
        if uploaded_file:
            st.success("✅ Resume uploaded successfully")
            try:
                file_details = {"Filename": uploaded_file.name, "Size": f"{uploaded_file.size / 1024:.2f} KB"}
                st.json(file_details)
            except:
                pass
    
    # Check and update inputs_ready status
    st.session_state.inputs_ready = bool(job_desc.strip() and uploaded_file)
    
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("<p>Select the Gemini model for your analysis:</p>", unsafe_allow_html=True)
        selected_model_label = st.selectbox(
            "AI Model:",
            list(model_options.keys()),
            index=0,
            help="Different models offer varying levels of analysis depth and speed"
        )
        model_choice = model_options[selected_model_label]
    
    st.markdown("<div class='section-header'>Analysis Options</div>", unsafe_allow_html=True)
    
    # Show ready status
    if st.session_state.inputs_ready:
        st.success("✅ Ready to analyze! Select an option below.")
    else:
        st.warning("⚠️ Please provide both a job description and resume before analysis.")
    
    # Organized buttons in tabs for better categorization
    tabs = st.tabs(["Basic Analysis", "Detailed Analysis", "Custom Query"])
    
    with tabs[0]:
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("✨ Resume Overview", use_container_width=True) and st.session_state.inputs_ready:
                response_output, response_time_taken = handle_response("submit1")
                if response_output:  # Only save if there's actual content
                    save_response_history(response_output, "Resume Overview")
                
        with col1b:
            if st.button("🎯 Match Percentage", use_container_width=True) and st.session_state.inputs_ready:
                result, response_time_taken = handle_response("submit4")
                if isinstance(result, tuple):
                    percentage, explanation = result
                    save_response_history(explanation, "Match Percentage")
                    
    with tabs[1]:
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("🚀 Skill Improvement", use_container_width=True) and st.session_state.inputs_ready:
                response_output, response_time_taken = handle_response("submit2")
                if response_output:
                    save_response_history(response_output, "Skill Improvement")
                
        with col2b:
            if st.button("🔍 Missing Keywords", use_container_width=True) and st.session_state.inputs_ready:
                response_output, response_time_taken = handle_response("submit3")
                if response_output:
                    save_response_history(response_output, "Missing Keywords")
                
        if st.button("👔 Interview Chances", use_container_width=True) and st.session_state.inputs_ready:
            response_output, response_time_taken = handle_response("submit5")
            if response_output:
                save_response_history(response_output, "Interview Chances")
            
    with tabs[2]:
        custom_query = st.text_input(
            "Ask a specific question:",
            placeholder="Example: What specific certifications would help me for this role?"
        )
        if st.button("🔮 Answer My Question", use_container_width=True) and custom_query and st.session_state.inputs_ready:
            response_output, response_time_taken = handle_response(custom_query)
            if response_output:
                save_response_history(response_output, f"Custom: {custom_query}")

with col2:
    st.markdown("<div class='section-header'>Analysis Results</div>", unsafe_allow_html=True)
    
    # Only show analysis results if inputs are ready
    if st.session_state.inputs_ready:
        # Display specific percentage match if available
        if 'response_history' in st.session_state and any(item["type"] == "Match Percentage" for item in st.session_state.response_history):
            # Find the most recent match percentage
            match_item = next((item for item in reversed(st.session_state.response_history) if item["type"] == "Match Percentage"), None)
            if match_item:
                match = re.search(r"(\d{1,3})\s*%", match_item["response"])
                percentage = int(match.group(1)) if match else None
                
                if percentage is not None:
                    st.metric(
                        "Resume-Job Description Match", 
                        f"{percentage}%",
                        delta=None
                    )
                    
                    # Color-coded progress bar
                    color = "green" if percentage >= 70 else "orange" if percentage >= 50 else "red"
                    st.progress(percentage / 100)
                    
                    match_text = "Excellent Match" if percentage >= 85 else \
                                "Good Match" if percentage >= 70 else \
                                "Fair Match" if percentage >= 50 else \
                                "Needs Improvement"
                                
                    st.info(f"**Match Quality:** {match_text}")
        
        # Response history
        if 'response_history' in st.session_state and st.session_state.response_history:
            for item in reversed(st.session_state.response_history):
                with st.expander(f"{item['type']} ({item['timestamp']})"):
                    st.write(item['response'])
        else:
            st.info("📊 Click an analysis option to see results here.")
    else:
        # Show instructions when inputs are not ready
        st.info("📋 Complete both required inputs to begin analysis:")
        st.markdown("""
        1. Paste the job description
        2. Upload your resume (PDF format)
        
        Once both are provided, analysis options will become available.
        """)
            
        with st.expander("📚 How to get started"):
            st.markdown("""
            1. Paste the job description in the text area
            2. Upload your resume PDF
            3. Choose an analysis option from the tabs
            4. View your results in this panel
            """)
            
# Footer
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("**JobFit Analyzer** - Powered by Gemini AI")
st.markdown("*Disclaimer: This application is for educational purposes only and does not guarantee job placement or success.*")
st.markdown("</div>", unsafe_allow_html=True)