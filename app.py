import os
import tempfile
import streamlit as st

from tools import parse_resume
from pipeline import run_placement_pipeline

# 1. Page Configuration
st.set_page_config(
    page_title="RoleFit AI",
    page_icon="🎯",
    layout="wide"
)

# 2. Custom CSS Theme
st.markdown("""
<style>
    /* Main Dark Slate Background */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Header Styling */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    
    /* Input Form Cards */
    div[data-testid="stForm"], div.stCard {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Pipeline Status Card */
    .status-panel {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
    }
    
    .status-step {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .badge-done {
        color: #10B981;
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid #10B981;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .badge-running {
        color: #3B82F6;
        background-color: rgba(59, 130, 246, 0.1);
        border: 1px solid #3B82F6;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .badge-waiting {
        color: #64748B;
        background-color: rgba(100, 116, 139, 0.1);
        border: 1px solid #475569;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Prominent Skill Gap Highlight Box */
    .skill-gap-highlight {
        background-color: rgba(59, 130, 246, 0.08);
        border: 2px solid #3B82F6;
        border-radius: 12px;
        padding: 24px;
        margin-top: 24px;
        margin-bottom: 24px;
    }
    
    .skill-gap-title {
        color: #60A5FA;
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    /* Primary Button Styling */
    div.stButton > button[kind="primary"] {
        background-color: #2563EB;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# 3. Session State Initialization
if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = {
        "company_research": "waiting",
        "interview_patterns": "waiting",
        "skill_gap": "waiting",
        "final_report": "waiting"
    }

if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None

if "error_message" not in st.session_state:
    st.session_state.error_message = None

# Header Section
st.markdown('<div class="main-title">🎯 RoleFit AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Automate candidate company intelligence, interview questions, and customized prep reports.</div>', unsafe_allow_html=True)

# 4. Main Two-Column Layout
col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.markdown("### 📝 Preparation Inputs")
    company_name = st.text_input("Target Company Name", placeholder="e.g. Stripe, Canva, Google")
    company2_name = st.text_input("Compare with another company (Optional)", placeholder="e.g. Apple, Meta (optional)")
    role_name = st.text_input("Target Role Name", placeholder="e.g. Software Engineer, Product Manager")
    jd_input = st.text_area("Job Description or Career URL", placeholder="Paste the job requirements text or enter a public career link...", height=160)
    resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
    
    st.caption("⚠️ Note: Uses external API quota — avoid rapid repeated runs during testing.")
    run_clicked = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

with col2:
    st.markdown("### ⚙️ Pipeline Progress Status")
    
    steps_info = [
        ("company_research", "1. Company Research"),
        ("interview_patterns", "2. Interview Patterns"),
        ("skill_gap", "3. Skill Gap Analysis"),
        ("final_report", "4. Report Generation")
    ]
    
    for key, label in steps_info:
        current_state = st.session_state.pipeline_status.get(key, "waiting")
        if current_state == "done":
            badge_html = '<span class="badge-done">✅ Done</span>'
        elif current_state == "running":
            badge_html = '<span class="badge-running">⏳ Running...</span>'
        else:
            badge_html = '<span class="badge-waiting">⏳ Waiting</span>'
            
        st.markdown(
            f'<div class="status-step"><span>{label}</span>{badge_html}</div>',
            unsafe_allow_html=True
        )

# 5. Analysis Trigger Execution
if run_clicked:
    if not company_name or not role_name or not jd_input or not resume_file:
        st.error("Please fill in all inputs and upload a valid PDF resume.")
    else:
        st.session_state.error_message = None
        st.session_state.pipeline_results = None
        st.session_state.pipeline_status = {
            "company_research": "waiting",
            "interview_patterns": "waiting",
            "skill_gap": "waiting",
            "final_report": "waiting"
        }
        
        # Save uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(resume_file.getvalue())
            tmp_pdf_path = tmp_file.name
            
        try:
            # Parse resume PDF text
            extracted_resume_text = parse_resume.invoke(tmp_pdf_path)
            if extracted_resume_text.startswith("Error"):
                raise ValueError(extracted_resume_text)
                
            # Callback to update live status indicators
            def status_callback(step: str, state: str):
                st.session_state.pipeline_status[step] = state
            
            # Run sequential placement pipeline
            results = run_placement_pipeline(
                company=company_name,
                role=role_name,
                jd_text=jd_input,
                resume_text=extracted_resume_text,
                callback=status_callback,
                company2=company2_name if company2_name else None
            )
            
            st.session_state.pipeline_results = results
            st.rerun()
            
        except Exception as err:
            st.session_state.error_message = f"Pipeline error: {str(err)}"
        finally:
            if os.path.exists(tmp_pdf_path):
                os.remove(tmp_pdf_path)

# Display Error Message if any occurred
if st.session_state.error_message:
    st.error(st.session_state.error_message)

# 6. Results Section below
if st.session_state.pipeline_results:
    res = st.session_state.pipeline_results
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Expanders for raw data
    with st.expander("📂 Raw Company Research"):
        st.markdown(res.get("company_research", "N/A"))
        if res.get("company_research2"):
            st.markdown("---")
            st.markdown("### Secondary Company Research")
            st.markdown(res.get("company_research2"))
            
    with st.expander("📂 Raw Interview Patterns"):
        st.markdown(res.get("interview_patterns", "N/A"))
        if res.get("interview_patterns2"):
            st.markdown("---")
            st.markdown("### Secondary Interview Patterns")
            st.markdown(res.get("interview_patterns2"))
            
    # Prominently Displayed Skill Gap Section (Differentiator Feature)
    st.markdown(
        f'''
        <div class="skill-gap-highlight">
            <div class="skill-gap-title">🎯 Key Differentiator: Targeted Skill Gap Analysis</div>
            <div>Below is the direct resume-to-JD alignment score and missing skill breakdown for candidate preparation:</div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(res.get("skill_gap", "N/A"))
    st.markdown("---")
    
    # Final Markdown Report & Download
    final_report_text = res.get("final_report", "")
    # Clean initial thought blocks if present
    clean_report = final_report_text.replace("<thought>", "").replace("</thought>", "")
    
    report_col1, report_col2 = st.columns([0.7, 0.3])
    with report_col1:
        st.markdown("### 📄 Customized Preparation Report")
    with report_col2:
        st.download_button(
            label="📥 Download Report (.md)",
            data=clean_report,
            file_name=f"{company_name.lower().replace(' ', '_')}_prep_report.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    st.markdown(clean_report)
