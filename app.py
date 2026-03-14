import streamlit as st
import google.generativeai as genai
import json
import re
import pdfplumber
import io

st.set_page_config(
    page_title="HireSense AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Configuration error: API key not found.")
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background: #0F0F13 !important;
    color: #E2E2E9;
}
.stApp { background: #0F0F13 !important; }
#MainMenu, footer, header { visibility: hidden !important; }

.block-container {
    padding-top: 2.75rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.75rem !important;
    padding-right: 2.75rem !important;
    max-width: 920px !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0F0F13; }
::-webkit-scrollbar-thumb { background: #2A2A35; border-radius: 4px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #09090E !important;
    border-right: 1px solid #1C1C25 !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: #09090E !important;
    padding: 1.75rem 1.4rem !important;
}

/* Logo */
.logo-mark {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4338CA 0%, #7C3AED 100%);
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800; font-size: 16px; color: #fff;
    flex-shrink: 0;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35);
}
.logo-mark-lg {
    width: 48px; height: 48px;
    border-radius: 13px;
    background: linear-gradient(135deg, #4338CA 0%, #7C3AED 100%);
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800; font-size: 22px; color: #fff;
    flex-shrink: 0;
    box-shadow: 0 6px 20px rgba(99,102,241,0.4);
}

/* Labels */
.stTextArea > label, .stTextInput > label, .stFileUploader > label {
    font-family: 'Outfit', sans-serif !important;
    font-size: 10.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: #4A4A5A !important;
}

/* Textareas */
.stTextArea textarea {
    background: #141418 !important;
    border: 1px solid #1F1F2A !important;
    border-radius: 12px !important;
    color: #E2E2E9 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13.5px !important;
    line-height: 1.75 !important;
    padding: 0.9rem 1rem !important;
}
.stTextArea textarea:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
}
.stTextArea textarea::placeholder { color: #2A2A38 !important; }

/* Text input */
.stTextInput input {
    background: #141418 !important;
    border: 1px solid #1F1F2A !important;
    border-radius: 10px !important;
    color: #E2E2E9 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13.5px !important;
    padding: 0.65rem 1rem !important;
}
.stTextInput input:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
}
.stTextInput input::placeholder { color: #2A2A38 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #141418 !important;
    border: 1.5px dashed #1F1F2A !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #4F46E5 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: #4A4A5A !important; }

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg, #4338CA 0%, #6D28D9 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.72rem 2rem !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 18px rgba(79,70,229,0.28) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* Back button */
.back-btn .stButton > button {
    background: transparent !important;
    border: 1px solid #1F1F2A !important;
    color: #4A4A5A !important;
    box-shadow: none !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 12.5px !important;
    padding: 0.38rem 1rem !important;
    border-radius: 8px !important;
}
.back-btn .stButton > button:hover {
    background: transparent !important;
    border-color: #3A3A4A !important;
    color: #9696AA !important;
    transform: none !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

.stSpinner > div { border-top-color: #6366F1 !important; }
.stAlert {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    border-radius: 10px !important;
}
[data-testid="column"] { padding: 0 0.4rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_color(s):
    if s >= 8: return "#34D399"
    if s >= 5: return "#FBBF24"
    return "#F87171"

def get_label(s):
    if s >= 8: return "Strong Resume"
    if s >= 5: return "Needs Improvement"
    return "Significant Work Needed"

def get_badge(s):
    if s >= 8:
        return "background:rgba(52,211,153,0.1);color:#34D399;border:1px solid rgba(52,211,153,0.25);"
    if s >= 5:
        return "background:rgba(251,191,36,0.1);color:#FBBF24;border:1px solid rgba(251,191,36,0.25);"
    return "background:rgba(248,113,113,0.1);color:#F87171;border:1px solid rgba(248,113,113,0.25);"

def ring_svg(score, color):
    r = 48
    circ = 2 * 3.14159265 * r
    offset = circ * (1 - score / 10)
    return f"""
    <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <circle cx="60" cy="60" r="{r}" fill="none" stroke="#1C1C25" stroke-width="9"/>
      <circle cx="60" cy="60" r="{r}" fill="none" stroke="{color}" stroke-width="9"
        stroke-linecap="round"
        stroke-dasharray="{circ:.1f}"
        stroke-dashoffset="{offset:.1f}"
        transform="rotate(-90 60 60)"/>
    </svg>"""

def extract_pdf_text(uploaded_file):
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def run_analysis(resume_text, job_title, job_desc):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    jd_section = f"""
TARGET JOB TITLE: {job_title}
JOB DESCRIPTION:
{job_desc}
""" if job_desc.strip() else f"TARGET JOB TITLE: {job_title}" if job_title.strip() else "No job description provided."

    prompt = f"""You are a world-class resume expert, career coach, and ATS specialist. Analyze the following resume thoroughly.

RESUME:
{resume_text}

{jd_section}

Respond ONLY with a valid JSON object — no markdown, no backticks, no extra text:
{{
  "rating": <integer 1-10 for overall clarity and impact>,
  "ratingJustification": "<one sentence explaining the rating>",
  "professionalSummary": "<exactly 2 lines: a powerful, professional summary the candidate can put at the top of their resume>",
  "extractedSkills": ["<skill1>","<skill2>","<skill3>","<skill4>","<skill5>","<skill6>","<skill7>","<skill8>"],
  "extractedKeywords": ["<kw1>","<kw2>","<kw3>","<kw4>","<kw5>","<kw6>"],
  "extractedProjects": ["<project name and one line description>","<project name and one line description>","<project name and one line description>"],
  "sectionImprovements": {{
    "summary": "<specific suggestion to improve or add the summary section>",
    "experience": "<specific suggestion to improve experience section with action verbs and metrics>",
    "skills": "<specific suggestion to improve skills section>",
    "projects": "<specific suggestion to improve projects section>",
    "education": "<specific suggestion to improve education section>"
  }},
  "improvementTask": "<one clear task the candidate must do to push their resume score to 8 or above>",
  "matchedKeywords": ["<jd keyword found in resume 1>","<jd keyword found in resume 2>","<jd keyword found in resume 3>","<jd keyword found in resume 4>"],
  "missingKeywords": ["<important jd keyword missing from resume 1>","<missing kw 2>","<missing kw 3>","<missing kw 4>","<missing kw 5>"],
  "alignmentScore": <integer 0-100 representing how well the resume matches the job description>,
  "alignmentGaps": ["<gap 1>","<gap 2>","<gap 3>"]
}}

If no job description is provided, set matchedKeywords to [], missingKeywords to [], alignmentScore to 0, alignmentGaps to ["No job description provided"].
"""
    resp = model.generate_content(prompt, generation_config={"temperature": 0.2})
    clean = re.sub(r"```json|```", "", resp.text.strip()).strip()
    return json.loads(clean)


# ── Session state ─────────────────────────────────────────────────────────────
if "result"      not in st.session_state: st.session_state.result      = None
if "show_result" not in st.session_state: st.session_state.show_result = False
if "prev_score"  not in st.session_state: st.session_state.prev_score  = None
if "job_title"   not in st.session_state: st.session_state.job_title   = ""
if "job_desc_s"  not in st.session_state: st.session_state.job_desc_s  = ""
if "is_reeval"   not in st.session_state: st.session_state.is_reeval   = False


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:11px;margin-bottom:1.75rem;padding-bottom:1.5rem;border-bottom:1px solid #1C1C25;">
        <div class="logo-mark">H</div>
        <div>
            <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1rem;font-weight:700;color:#E2E2E9;letter-spacing:-0.01em;">HireSense AI</div>
            <div style="font-size:11px;color:#3A3A4A;margin-top:2px;">Resume Intelligence</div>
        </div>
    </div>
    <div style="font-size:10px;letter-spacing:0.18em;text-transform:uppercase;color:#2A2A38;font-weight:600;margin-bottom:0.75rem;">What it analyzes</div>
    """, unsafe_allow_html=True)

    features = [
        ("#6366F1", "Resume Rating",         "Scores your resume out of 10 for clarity and impact"),
        ("#34D399", "Extracted Highlights",   "Skills, keywords, and projects pulled from your resume"),
        ("#FBBF24", "Section Improvements",   "Specific suggestions for every section of your resume"),
        ("#F87171", "Professional Summary",   "AI-generated 2-line summary ready to use"),
        ("#A78BFA", "JD Alignment",           "Matches your resume against the target job description"),
    ]
    for clr, title, desc in features:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:10px;padding:0.65rem 0;border-bottom:1px solid #141420;">
            <div style="width:8px;height:8px;border-radius:50%;background:{clr};margin-top:5px;flex-shrink:0;box-shadow:0 0 6px {clr}66;"></div>
            <div>
                <div style="font-size:12.5px;font-weight:500;color:#C4C4D0;margin-bottom:2px;">{title}</div>
                <div style="font-size:11px;color:#3A3A4A;line-height:1.5;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1.25rem;border-top:1px solid #1C1C25;">
        <div style="font-size:11px;color:#2E2E3A;">Powered by Google Gemini AI</div>
        <div style="display:flex;align-items:center;gap:6px;margin-top:7px;">
            <span style="width:6px;height:6px;background:#34D399;border-radius:50%;display:inline-block;"></span>
            <span style="font-size:11px;color:#3A3A4A;">All systems operational</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.show_result:

    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:0.6rem;">
        <div class="logo-mark-lg">H</div>
        <div>
            <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.85rem;font-weight:800;color:#E2E2E9;letter-spacing:-0.03em;line-height:1.1;">HireSense AI</div>
            <div style="font-size:13px;color:#4A4A5A;margin-top:3px;">Resume Intelligence Platform</div>
        </div>
    </div>
    <div style="font-size:13.5px;color:#4A4A5A;line-height:1.75;margin-bottom:2rem;max-width:580px;">
        Upload your resume as a PDF. Get an instant rating, extracted highlights, section-by-section improvements, a ready-to-use professional summary, and alignment analysis against any job description.
    </div>
    """, unsafe_allow_html=True)

    # Re-eval banner
    if st.session_state.is_reeval and st.session_state.prev_score is not None:
        prev = st.session_state.prev_score
        st.markdown(f"""
        <div style="background:rgba(251,191,36,0.06);border:1px solid rgba(251,191,36,0.2);border-radius:12px;padding:1rem 1.25rem;margin-bottom:1.25rem;display:flex;align-items:center;gap:1rem;">
            <div style="font-size:1.6rem;font-weight:800;font-family:'Bricolage Grotesque',sans-serif;color:#FBBF24;">{prev}/10</div>
            <div>
                <div style="font-size:12.5px;font-weight:600;color:#FBBF24;">Previous Score</div>
                <div style="font-size:12px;color:#5A5A6A;margin-top:2px;">Upload your improved resume to see how much your score has increased.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # PDF Upload
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Job title + JD
    job_title = st.text_input(
        "Target Job Title",
        placeholder="e.g. Full Stack Developer, Data Scientist, Product Manager...",
    )

    job_desc = st.text_area(
        "Job Description (optional but recommended)",
        placeholder="Paste the job description here to get alignment analysis and missing keyword suggestions...",
        height=200,
    )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    btn_col, _ = st.columns([1, 1])
    with btn_col:
        if st.button("Analyze Resume"):
            if not uploaded_file:
                st.error("Please upload your resume as a PDF.")
            elif not job_title.strip():
                st.error("Please enter your target job title.")
            else:
                with st.spinner("Extracting and analyzing your resume..."):
                    try:
                        resume_text = extract_pdf_text(uploaded_file)
                        if not resume_text.strip():
                            st.error("Could not extract text from the PDF. Make sure it is not a scanned image.")
                        else:
                            result = run_analysis(resume_text, job_title, job_desc)
                            st.session_state.result = result
                            st.session_state.show_result = True
                            st.rerun()
                    except json.JSONDecodeError:
                        st.error("Unexpected AI response. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS SCREEN
# ══════════════════════════════════════════════════════════════════════════════
else:
    r     = st.session_state.result
    score = r.get("rating", 0)
    color = get_color(score)
    label = get_label(score)
    badge = get_badge(score)

    back_col, reeval_col, _ = st.columns([1, 1, 2])
    with back_col:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("New Analysis"):
            st.session_state.result = None
            st.session_state.show_result = False
            st.session_state.prev_score = None
            st.session_state.is_reeval = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with reeval_col:
        if st.button("Re-evaluate Resume"):
            st.session_state.prev_score = st.session_state.result.get("rating", 0)
            st.session_state.is_reeval = True
            st.session_state.result = None
            st.session_state.show_result = False
            st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.5rem;font-weight:700;color:#E2E2E9;letter-spacing:-0.025em;margin-bottom:1.25rem;">
        Resume Analysis Report
    </div>""", unsafe_allow_html=True)

    # ── Score card ──
    svg = ring_svg(score, color)
    st.markdown(f"""
    <div style="background:#111118;border:1px solid #1C1C25;border-radius:18px;padding:1.85rem 2.25rem;display:flex;align-items:center;gap:2.25rem;margin-bottom:1rem;box-shadow:0 4px 24px rgba(0,0,0,0.3);flex-wrap:wrap;">
        <div style="position:relative;width:120px;height:120px;flex-shrink:0;">
            {svg}
            <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
                <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:2.6rem;font-weight:800;line-height:1;color:{color};">{score}</div>
                <div style="font-size:11px;color:#2E2E3A;margin-top:3px;">/ 10</div>
            </div>
        </div>
        <div style="flex:1;min-width:200px;">
            <span style="display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:3px 11px;border-radius:99px;margin-bottom:0.65rem;{badge}">{label}</span>
            <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.3rem;font-weight:700;color:#E2E2E9;line-height:1.3;letter-spacing:-0.02em;margin-bottom:0.6rem;">{r.get("ratingJustification","")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score improvement banner (re-eval) ──
    prev = st.session_state.prev_score
    if prev is not None:
        diff = score - prev
        diff_color = "#34D399" if diff > 0 else "#F87171" if diff < 0 else "#FBBF24"
        diff_text  = f"+{diff}" if diff > 0 else str(diff)
        msg = "Great improvement! Keep refining." if diff > 0 else "Score unchanged. Apply the suggestions below and try again." if diff == 0 else "Score dropped. Review the suggestions carefully."
        st.markdown(f"""
        <div style="background:#111118;border:1px solid {diff_color}33;border-radius:14px;padding:1.1rem 1.5rem;margin-bottom:1rem;display:flex;align-items:center;gap:1.5rem;">
            <div style="text-align:center;flex-shrink:0;">
                <div style="font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#2E2E3A;margin-bottom:4px;">Score Change</div>
                <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:2rem;font-weight:800;color:{diff_color};">{diff_text}</div>
            </div>
            <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;">
                <div style="text-align:center;"><div style="font-size:10px;color:#2E2E3A;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Previous</div><div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.5rem;font-weight:700;color:#5A5A6A;">{prev}/10</div></div>
                <div style="font-size:1.5rem;color:#2E2E3A;">→</div>
                <div style="text-align:center;"><div style="font-size:10px;color:#2E2E3A;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Current</div><div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.5rem;font-weight:700;color:{diff_color};">{score}/10</div></div>
                <div style="font-size:13px;color:#5A5A6A;">{msg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Professional Summary ──
    st.markdown(f"""
    <div style="background:#111118;border:1px solid #4338CA44;border-radius:16px;padding:1.35rem 1.75rem;margin-bottom:1rem;">
        <div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:#6366F1;font-weight:700;margin-bottom:0.75rem;">AI-Generated Professional Summary</div>
        <div style="font-size:14.5px;color:#C4C4D0;line-height:1.8;font-style:italic;">"{r.get("professionalSummary","")}"</div>
        <div style="font-size:11px;color:#2E2E3A;margin-top:0.75rem;">Copy this to the top of your resume.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Extracted highlights ──
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1rem;font-weight:700;color:#E2E2E9;letter-spacing:-0.01em;margin-bottom:0.75rem;">Extracted Highlights</div>""", unsafe_allow_html=True)

    hc1, hc2, hc3 = st.columns(3, gap="medium")
    with hc1:
        tags = "".join([
            f'<span style="display:inline-flex;padding:4px 10px;border-radius:7px;font-size:12px;font-weight:500;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);color:#818CF8;margin:3px 3px 3px 0;">{s}</span>'
            for s in r.get("extractedSkills", [])
        ])
        st.markdown(f"""
        <div style="background:#111118;border:1px solid #1C1C25;border-radius:16px;padding:1.25rem 1.4rem;">
            <div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:#2E2E3A;font-weight:600;margin-bottom:0.85rem;">Skills</div>
            <div>{tags}</div>
        </div>""", unsafe_allow_html=True)

    with hc2:
        tags = "".join([
            f'<span style="display:inline-flex;padding:4px 10px;border-radius:7px;font-size:12px;font-weight:500;background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);color:#34D399;margin:3px 3px 3px 0;">{k}</span>'
            for k in r.get("extractedKeywords", [])
        ])
        st.markdown(f"""
        <div style="background:#111118;border:1px solid #1C1C25;border-radius:16px;padding:1.25rem 1.4rem;">
            <div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:#2E2E3A;font-weight:600;margin-bottom:0.85rem;">Keywords</div>
            <div>{tags}</div>
        </div>""", unsafe_allow_html=True)

    with hc3:
        projects = r.get("extractedProjects", [])
        proj_rows = "".join([
            f'<div style="font-size:12.5px;color:#9A9AAA;padding:0.4rem 0;border-bottom:1px solid #14141E;line-height:1.5;">{p}</div>'
            for p in projects
        ])
        st.markdown(f"""
        <div style="background:#111118;border:1px solid #1C1C25;border-radius:16px;padding:1.25rem 1.4rem;">
            <div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:#2E2E3A;font-weight:600;margin-bottom:0.85rem;">Projects</div>
            {proj_rows if proj_rows else '<div style="font-size:12.5px;color:#3A3A4A;">No projects detected.</div>'}
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Section Improvements ──
    st.markdown("""<div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1rem;font-weight:700;color:#E2E2E9;letter-spacing:-0.01em;margin-bottom:0.75rem;">Section-by-Section Improvements</div>""", unsafe_allow_html=True)

    improvements = r.get("sectionImprovements", {})
    section_colors = {
        "summary":    "#6366F1",
        "experience": "#34D399",
        "skills":     "#FBBF24",
        "projects":   "#F87171",
        "education":  "#A78BFA",
    }
    section_labels = {
        "summary":    "Summary",
        "experience": "Experience",
        "skills":     "Skills",
        "projects":   "Projects",
        "education":  "Education",
    }

    ic1, ic2 = st.columns(2, gap="medium")
    items = list(improvements.items())
    for i, (section, suggestion) in enumerate(items):
        col = ic1 if i % 2 == 0 else ic2
        clr = section_colors.get(section, "#6366F1")
        lbl = section_labels.get(section, section.title())
        with col:
            st.markdown(f"""
            <div style="background:#111118;border:1px solid #1C1C25;border-radius:14px;padding:1.1rem 1.3rem;margin-bottom:0.75rem;border-left:3px solid {clr};">
                <div style="font-size:10.5px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:{clr};margin-bottom:0.5rem;">{lbl}</div>
                <div style="font-size:13px;color:#9A9AAA;line-height:1.65;">{suggestion}</div>
            </div>""", unsafe_allow_html=True)

    # ── Improvement Task ──
    task = r.get("improvementTask", "")
    if task:
        st.markdown(f"""
        <div style="background:#0D0D14;border:1px solid #FBBF2433;border-radius:14px;padding:1.25rem 1.5rem;margin-bottom:1rem;">
            <div style="font-size:10.5px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#FBBF24;margin-bottom:0.6rem;">Your Task to Reach 8+/10</div>
            <div style="font-size:13.5px;color:#C4C4D0;line-height:1.7;">{task}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── JD Alignment ──
    alignment = r.get("alignmentScore", 0)
    gaps      = r.get("alignmentGaps", [])
    matched   = r.get("matchedKeywords", [])
    missing   = r.get("missingKeywords", [])

    if alignment > 0:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Bricolage Grotesque',sans-serif;font-size:1rem;font-weight:700;color:#E2E2E9;letter-spacing:-0.01em;margin-bottom:0.75rem;">Job Description Alignment</div>""", unsafe_allow_html=True)

        a_color = "#34D399" if alignment >= 70 else "#FBBF24" if alignment >= 40 else "#F87171"
        st.markdown(f"""
        <div style="background:#111118;border:1px solid #1C1C25;border-radius:16px;padding:1.5rem 1.75rem;margin-bottom:0.85rem;display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;">
            <div style="text-align:center;flex-shrink:0;">
                <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:2.8rem;font-weight:800;color:{a_color};line-height:1;">{alignment}%</div>
                <div style="font-size:11px;color:#2E2E3A;margin-top:3px;">Alignment Score</div>
            </div>
            <div style="flex:1;min-width:200px;">
                {"".join([f'<div style="display:flex;align-items:flex-start;gap:0.6rem;padding:0.4rem 0;border-bottom:1px solid #14141E;font-size:13px;color:#9A9AAA;line-height:1.5;"><span style="color:#F87171;margin-top:2px;font-weight:700;flex-shrink:0;">-</span><span>{g}</span></div>' for g in gaps])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        kc1, kc2 = st.columns(2, gap="medium")
        with kc1:
            tags = "".join([
                f'<span style="display:inline-flex;padding:4px 11px;border-radius:7px;font-size:12px;font-weight:500;background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);color:#34D399;margin:3px 3px 3px 0;">{k}</span>'
                for k in matched
            ])
            st.markdown(f'<div style="background:#111118;border:1px solid #1C1C25;border-radius:16px;padding:1.25rem 1.4rem;"><div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:#2E2E3A;font-weight:600;margin-bottom:0.85rem;">Matched Keywords</div><div>{tags}</div></div>', unsafe_allow_html=True)
        with kc2:
            tags = "".join([
                f'<span style="display:inline-flex;padding:4px 11px;border-radius:7px;font-size:12px;font-weight:500;background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.2);color:#F87171;margin:3px 3px 3px 0;">{k}</span>'
                for k in missing
            ])
            st.markdown(f'<div style="background:#111118;border:1px solid #1C1C25;border-radius:16px;padding:1.25rem 1.4rem;"><div style="font-size:10.5px;letter-spacing:0.16em;text-transform:uppercase;color:#2E2E3A;font-weight:600;margin-bottom:0.85rem;">Missing Keywords</div><div>{tags}</div></div>', unsafe_allow_html=True)