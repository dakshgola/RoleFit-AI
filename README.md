# RoleFit AI

> **A multi-agent AI system that researches target companies, analyzes interview patterns, and matches your resume against job descriptions to generate a personalized placement prep report.**

[🚀 Live Demo](https://rolefit-ai-5pafls932299wgs2ovtu2g.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=flat-square&logo=chainlink&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-Pro-8E75C2?style=flat-square&logo=google&logoColor=white)

---

## 🎯 What It Does

RoleFit AI automates the job interview preparation workflow by deploying autonomous AI agents to research target organizations, discover recent interview formats and community-shared questions (from Glassdoor, Reddit, and LeetCode Discuss), and construct a 14-day study plan tailored to the applicant's exact technical profile.

---

## ⭐ Key Feature: Resume-JD Skill Gap Analysis

Unlike standard research tools that only output static company trivia, **RoleFit AI performs a direct, line-by-line comparison between the candidate's PDF resume and the target Job Description.**

It calculates an **Estimated Readiness Score**, extracts exact matched and missing technical skills (e.g., PostgreSQL vs. MySQL, system design concepts, frameworks), and generates an actionable **2-week preparation calendar** designed exclusively to bridge those specific background gaps before the interview.

---

## ⚙️ How It Works

```text
Company Name + Role + JD + Resume
               │
               ▼
   ┌───────────────────────┐
   │ Company Research Agent│ (Web Search & Tavily Scraping)
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │Interview Pattern Agent│ (Glassdoor / Reddit / LeetCode Discuss Mining)
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │Skill Gap AnalysisChain│ (Resume PDF Parsing vs. JD Keyword Matching)
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │  Report Writer Chain  │ (Markdown Preparation Report Generation)
   └───────────┬───────────┘
               │
               ▼
    Final Prep Report (.md)
```

---

## 🛠️ Tech Stack

- **Core Language**: Python 3.9+
- **Frontend Dashboard**: Streamlit
- **Agentic Framework**: LangChain
- **LLM Engine**: Google Gemini API (`gemma-4-31b-it` / `gemini-1.5-pro`)
- **Search & Scraping API**: Tavily Search API, BeautifulSoup4
- **PDF Extraction**: PyPDF

---

## 🚀 Setup & Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/dakshgola/RoleFit-AI.git
cd RoleFit-AI
```

### 2. Set Up Virtual Environment & Dependencies

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Launch the App
```bash
streamlit run app.py
```
*(Or if running directly via virtual environment Python: `.\venv\Scripts\python.exe -m streamlit run app.py`)*
