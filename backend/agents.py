import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from tools import web_search, scrape_url

from langchain_core.callbacks import BaseCallbackHandler
from datetime import datetime
from rich import print as rprint

class LoggingCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized: dict, prompts: list, **kwargs) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        rprint(f"[bold cyan][{timestamp}] Gemini API Call Initiated[/bold cyan] - Prompts count: {len(prompts)}")

def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Initialize ChatOpenAI targeting Gemini's OpenAI-compatible endpoint, using Gemma model to support tool-calling without thought signature errors."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")
    return ChatOpenAI(
        model="gemma-4-31b-it",
        temperature=temperature,
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        callbacks=[LoggingCallbackHandler()]
    )

def build_company_research_agent():
    """Create a company research agent graph equipped with web search tool."""
    llm = get_llm(temperature=0.0)
    system_prompt = (
        "You are an elite Corporate Research Intelligence Agent. Your goal is to gather deep, comprehensive "
        "information about a target company. You must search for their core products/services, their primary "
        "business domain, recent news, company culture, values, and engineering or operational standards. "
        "Use the web_search tool to find recent, reliable sources. Synthesize your findings into a detailed summary."
    )
    return create_agent(model=llm, tools=[web_search], system_prompt=system_prompt)

def build_interview_pattern_agent():
    """Create an interview pattern discovery agent graph equipped with web search and scraping tools."""
    llm = get_llm(temperature=0.0)
    system_prompt = (
        "You are an expert Technical Interview Analyst. Your objective is to discover the interview process, "
        "round formats, structure, and actual question patterns for a target company and role. Use web_search "
        "to find interview experiences, preparation articles, and glassdoor reviews. Use scrape_url to fetch "
        "details from specific article links. Analyze what rounds are conducted, how candidates are evaluated, "
        "and compile likely interview questions. Make sure to scrape any high-relevance URLs you find."
    )
    return create_agent(model=llm, tools=[web_search, scrape_url], system_prompt=system_prompt)

# Skill Gap Analysis Chain
skill_gap_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Senior Technical Recruiter and Career Coach. Your job is to conduct a highly precise "
        "gap analysis comparing a candidate's resume against a target job description (JD).\n\n"
        "Be specific — name exact technologies, frameworks, languages, or concepts from the JD that are matched or missing "
        "from the resume. Do NOT use vague categories or phrases like 'more experience needed' or 'stronger background'. "
        "Every matched or missing item must map to a specific keyword or direct requirement in the JD.\n\n"
        "You must output exactly four sections:\n"
        "1. **Matched Skills**: Technical and soft skills present in both the resume and the job description.\n"
        "2. **Missing/Weak Skills**: Crucial skills, tools, or qualifications requested in the job description that are absent or poorly represented in the resume.\n"
        "3. **Priority to Learn**: Top 3 ranked skills or concepts the candidate should prioritize learning or improving, along with a brief rationale for each.\n"
        "4. **Estimated Readiness**: A score out of 10 representing how ready the candidate is for this role based solely on the resume alignment, with a 1-sentence justification."
    )),
    ("human", (
        "Here is the Job Description:\n"
        "<job_description>\n"
        "{jd_text}\n"
        "</job_description>\n\n"
        "Here is the Candidate's Resume:\n"
        "<resume>\n"
        "{resume_text}\n"
        "</resume>\n\n"
        "Please perform the skill gap analysis."
    ))
])

skill_gap_chain = skill_gap_prompt | get_llm(temperature=0.0) | StrOutputParser()

# Final Report Writer Chain
report_writer_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Master Career Strategist and Report Writer. Your task is to compile all the research, "
        "interview patterns, and skill gap analysis into a unified, high-value, tailored Placement Preparation Report.\n\n"
        "You must output a beautifully formatted Markdown document containing EXACTLY these sections:\n\n"
        "## Company Snapshot\n"
        "[Provide a detailed overview of the primary company, their main products, business model, and culture/values based on the research.]\n\n"
        "## ⚖️ Side-by-Side Company Comparison\n"
        "[ONLY include this section if details for a second company (company2, company_research2, and interview_patterns2) are provided. "
        "Render a markdown table comparing: Company Culture, Interview Difficulty, and Skill Fit Alignment (which company better "
        "matches the candidate's current resume skills based on the skill gap analysis). Provide a brief explanation beneath the table. "
        "If no second company details are provided, OMIT this section entirely.]\n\n"
        "## 🎯 Targeted Skill Gap Analysis & 2-Week Preparation Plan\n"
        "[PROMINENT SECTION: Directly summarize the critical skill gaps identified between the candidate's resume and the job description. "
        "Then, map out a custom, high-impact day-by-day 2-week preparation schedule designed specifically to bridge these gaps before the interview.]\n\n"
        "## Interview Format & Rounds\n"
        "[Break down the interview rounds, typical durations, and what is tested in each round based on the interview patterns. "
        "If a second company is provided, include details for both companies in separate subheadings.]\n\n"
        "## Likely Questions by round\n"
        "[List candidate questions they are likely to encounter in each round, including technical, behavioral, and system design, customized to the companies, roles, and the candidate's specific background gaps.]\n\n"
        "## Final Checklist\n"
        "[Provide a checklist of 5-7 actionable items the candidate must do before the interview to ensure success.]"
    )),
    ("human", (
        "Please write the final preparation report for:\n"
        "Primary Company: {company}\n"
        "Role: {role}\n\n"
        "Use the following gathered inputs:\n"
        "### Primary Company Research:\n"
        "{company_research}\n\n"
        "### Primary Company Interview Patterns:\n"
        "{interview_patterns}\n\n"
        "### Skill Gap Analysis:\n"
        "{skill_gap}\n\n"
        "### Optional Second Company (Comparison):\n"
        "Second Company Name: {company2}\n"
        "Second Company Research: {company_research2}\n"
        "Second Company Interview Patterns: {interview_patterns2}\n\n"
        "Ensure the report is detailed, tailored, and uses clean, structured markdown."
    ))
])

report_writer_chain = report_writer_prompt | get_llm(temperature=0.0) | StrOutputParser()
