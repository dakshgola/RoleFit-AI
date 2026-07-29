import os
from dotenv import load_dotenv
from agents import (
    build_company_research_agent,
    build_interview_pattern_agent,
    skill_gap_chain,
    report_writer_chain
)
from tools import scrape_url

# Load environment variables
load_dotenv()

class PlacementPrepPipeline:
    """Orchestrates company research, interview pattern mining, and skill gap analysis to generate a prep report."""
    
    def __init__(self):
        # Validate critical API keys before running
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")
            
        # Build agents
        self.company_agent = build_company_research_agent()
        self.interview_agent = build_interview_pattern_agent()
        
    def research_company(self, company_name: str) -> str:
        """Run the company research agent graph."""
        query = (
            f"Research the company '{company_name}'. Provide detailed information about its business model, "
            f"recent news, culture, and typical tech stack."
        )
        result = self.company_agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        return result["messages"][-1].content
        
    def research_interview_patterns(self, company_name: str, role_name: str) -> str:
        """Run the interview patterns agent graph."""
        query = (
            f"Analyze the interview process, rounds, and typical questions for a '{role_name}' role at '{company_name}'. "
            f"Search for Glassdoor, Reddit, and LeetCode Discuss style sources to find common question topics and structures."
        )
        result = self.interview_agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        return result["messages"][-1].content
        
    def run(self, company: str, role: str, resume_text: str, jd_text_or_url: str) -> dict:
        """Execute the full pipeline: company research, interview research, skill gap analysis, and compilation."""
        # Check if job description is a URL and scrape if so
        jd_text = jd_text_or_url
        if jd_text_or_url.strip().startswith(("http://", "https://")):
            print(f"Detected URL. Scraping job description from: {jd_text_or_url}")
            scraped_result = scrape_url.invoke(jd_text_or_url)
            if not scraped_result.startswith("Error"):
                jd_text = scraped_result
            else:
                print(f"Scraping failed: {scraped_result}. Using URL text directly.")
                
        # 1. Company Research
        print(f"Running company research for '{company}'...")
        company_research = self.research_company(company)
        
        # 2. Interview Patterns
        print(f"Running interview patterns mining for '{role}' at '{company}'...")
        interview_patterns = self.research_interview_patterns(company, role)
        
        # 3. Skill Gap Analysis
        print("Running resume skill gap analysis...")
        skill_gap = skill_gap_chain.invoke({
            "jd_text": jd_text,
            "resume_text": resume_text
        })
        
        # 4. Final Report Compilation
        print("Compiling final customized preparation report...")
        final_report = report_writer_chain.invoke({
            "company": company,
            "role": role,
            "company_research": company_research,
            "interview_patterns": interview_patterns,
            "skill_gap": skill_gap
        })
        
        return {
            "company_research": company_research,
            "interview_patterns": interview_patterns,
            "skill_gap": skill_gap,
            "final_report": final_report
        }

def run_placement_pipeline(company: str, role: str, jd_text: str, resume_text: str, callback=None, company2: str = None) -> dict:
    """Runs the placement prep pipeline sequentially, logging progress and returning the final state dictionary."""
    state = {}
    pipeline = PlacementPrepPipeline()
    
    # 1. Company Research
    company2_log = f" and '{company2}'" if company2 else ""
    print(f"\n[1/4] Starting Company Research for '{company}'{company2_log}...")
    if callback:
        callback("company_research", "running")
    try:
        state["company_research"] = pipeline.research_company(company)
        if company2:
            print(f"Starting secondary Company Research for '{company2}'...")
            state["company_research2"] = pipeline.research_company(company2)
        else:
            state["company_research2"] = ""
        print("[DONE] Company Research Completed successfully.")
    except Exception as e:
        print(f"Company Research Step failed: {str(e)}")
        state["company_research"] = "Could not retrieve detailed company research — proceeding with target company name only."
        state["company_research2"] = ""
    if callback:
        callback("company_research", "done")
    
    # 2. Interview Patterns
    print(f"\n[2/4] Mining Interview Patterns for '{role}' at '{company}'{company2_log}...")
    if callback:
        callback("interview_patterns", "running")
    try:
        state["interview_patterns"] = pipeline.research_interview_patterns(company, role)
        if company2:
            print(f"Mining secondary Interview Patterns for '{role}' at '{company2}'...")
            state["interview_patterns2"] = pipeline.research_interview_patterns(company2, role)
        else:
            state["interview_patterns2"] = ""
        print("[DONE] Interview Patterns analysis Completed successfully.")
    except Exception as e:
        print(f"Interview Patterns Step failed: {str(e)}")
        state["interview_patterns"] = f"Could not retrieve detailed interview patterns for '{role}' at '{company}' — report will use company research only."
        state["interview_patterns2"] = ""
    if callback:
        callback("interview_patterns", "done")
    
    # 3. Skill Gap Analysis
    print("\n[3/4] Performing Resume Skill Gap Analysis...")
    if callback:
        callback("skill_gap", "running")
    try:
        state["skill_gap"] = skill_gap_chain.invoke({
            "jd_text": jd_text,
            "resume_text": resume_text
        })
        print("[DONE] Skill Gap Analysis Completed successfully.")
    except Exception as e:
        print(f"Skill Gap Step failed: {str(e)}")
        state["skill_gap"] = "Could not complete precise skill gap analysis — report will list basic requirements alignment based on best available data."
    if callback:
        callback("skill_gap", "done")
    
    # 4. Final Report Writing
    print("\n[4/4] Compiling Placement Preparation Report...")
    if callback:
        callback("final_report", "running")
    try:
        state["final_report"] = report_writer_chain.invoke({
            "company": company,
            "role": role,
            "company_research": state["company_research"],
            "interview_patterns": state["interview_patterns"],
            "skill_gap": state["skill_gap"],
            "company2": company2 if company2 else "",
            "company_research2": state.get("company_research2", ""),
            "interview_patterns2": state.get("interview_patterns2", "")
        })
        print("[DONE] Final customized report generated successfully.")
    except Exception as e:
        print(f"Final Report Step failed: {str(e)}")
        state["final_report"] = (
            f"# Placement Preparation Report: {role} at {company}\n\n"
            f"**Error**: Full preparation report could not be automatically compiled due to a pipeline step failure.\n\n"
            f"### Available Section Summaries\n\n"
            f"#### Company Insights\n{state.get('company_research', 'N/A')}\n\n"
            f"#### Interview Patterns\n{state.get('interview_patterns', 'N/A')}\n\n"
            f"#### Skill Gap Details\n{state.get('skill_gap', 'N/A')}"
        )
    if callback:
        callback("final_report", "done")
    
    return state

def read_file_content(path: str) -> str:
    """Utility to read text or PDF files from the local filesystem."""
    path = path.strip()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Specified path does not exist: {path}")
        
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

if __name__ == "__main__":
    print("==================================================")
    print("Placement Prep CLI Pipeline Test")
    print("==================================================")
    
    company_input = input("Enter Company Name: ").strip()
    role_input = input("Enter Target Role Name: ").strip()
    
    jd_file_path = input("Enter Job Description File Path (TXT/PDF or Scraped URL): ").strip()
    resume_file_path = input("Enter Resume File Path (TXT or PDF): ").strip()
    
    try:
        # Load JD content (could be a URL or file path)
        if jd_file_path.startswith(("http://", "https://")):
            print(f"Job Description is a URL. Content will be scraped dynamically during execution.")
            jd_data = jd_file_path
        else:
            jd_data = read_file_content(jd_file_path)
            print(f"[OK] Job Description read successfully ({len(jd_data)} characters).")
            
        # Load Resume content
        resume_data = read_file_content(resume_file_path)
        print(f"[OK] Resume read successfully ({len(resume_data)} characters).")
        
        # Run Pipeline
        pipeline_state = run_placement_pipeline(
            company=company_input,
            role=role_input,
            jd_text=jd_data,
            resume_text=resume_data
        )
        
        # Save output
        output_filename = f"{company_input.lower().replace(' ', '_')}_prep_report.md"
        with open(output_filename, "w", encoding="utf-8") as out_f:
            out_f.write(pipeline_state["final_report"])
            
        print("\n==================================================")
        print("Pipeline Executed Successfully!")
        print(f"Tailored prep report saved as: {output_filename}")
        print("==================================================")
        
    except Exception as err:
        print(f"\n[ERROR] Error during execution: {str(err)}")
