# ResumeRankr  
**AI-Powered Resume Analyzer for Job Matching & Skill Insights**

ResumeRankr is a Streamlit web app that uses Google Gemini AI to analyze resumes against job descriptions. It offers personalized analysis, ATS-style matching, skill improvement suggestions, and interview predictions — all while ensuring user privacy and security.

---

## Features

### AI-Powered Analysis
- **Resume Overview** – Strengths & weaknesses summary
- **Match Percentage** – AI-estimated resume-job fit
- **Skill Improvement** – Technical and soft skill suggestions
- **Missing Keywords** – ATS-style keyword gap check
- **Interview Chances** – Shortlisting likelihood (Yes/Maybe/Unlikely)
- **Custom Queries** – Ask resume-related career questions

### Privacy & Compliance
- **User Consent Required** before processing
- **Sensitive Data Detection** (e.g., SSNs, credit cards)
- **Manual Data Deletion** ("Clear My Data" button)
- **Auto Session Timeout** after 30 minutes of inactivity
- **GDPR-Aligned**: Rights info, clear notices, explicit consent

### Security
- **API Rate Limiting:** Max 50 requests per session
- **Session Tracking:** UUID-based identification
- **API Key Protection:** Uses `.env` for secure storage
- **Session Expiry Alerts:** Warnings before auto-clear

### Accessibility
- Keyboard navigation support  
- Screen reader compatibility  
- High contrast theme & ARIA attributes

### Additional Features
- **Download Results as Word (.docx)**
- **Session History with Timestamps**
- **Improved Error Handling** (PDF parsing, API, validation)

---

## Getting Started

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ResumeRankr.git
   cd ResumeRankr
   ```

2. **Create `.env` file** and add your [Google Gemini API key](https://ai.google.dev/)
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## Disclaimer

ResumeRankr is intended for educational use and does not guarantee job placement or accuracy of AI-generated results. Always verify outputs before professional use.
