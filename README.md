# HireSense AI — Resume Intelligence Platform

An AI-powered resume screening tool built with Streamlit and Google Gemini. Instantly analyzes how well a resume matches a job description and returns a structured, actionable report.

Built for the **Code the Future: AI Edition** hackathon by UnsaidTalks Education.

---

## Live Demo

https://hiresense--ai.streamlit.app/
---

## What It Does

HireSense AI uses Google Gemini to evaluate a candidate's resume against any job description and returns:

| Output | Description |
|---|---|
| Match Score (0-100) | ATS-style compatibility rating |
| Matched Keywords | Skills and terms already present in the resume |
| Missing Keywords | Important terms absent from the resume |
| Strengths | What the candidate does well relative to the role |
| Gaps | Areas where the candidate falls short |
| Actionable Tips | Concrete steps to improve the resume for the specific role |

---

## Problem It Solves

Most candidates apply to jobs without knowing how their resume performs against automated screening systems. Hiring teams reject the majority of applications before a human ever reads them. HireSense AI gives every candidate the same intelligence that recruiters use — in seconds, for free.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit |
| AI Model | Google Gemini 2.5 Flash |
| Language | Python 3.10+ |
| Deployment | Streamlit Community Cloud |

No backend server. No database. No login required. The API key is entered by the user and never stored.

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/hiresense-ai.git
cd hiresense-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Get a free Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

---

## Deploying to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo, set main file to `app.py`
4. Click Deploy — live in under 2 minutes

---

## Project Structure

```
hiresense-ai/
    app.py              Main Streamlit application
    requirements.txt    Python dependencies
    README.md           Project documentation
```

---

## Author

Built by Bhuvan Bhonde — Code the Future: AI Edition, UnsaidTalks Education Hackathon.
