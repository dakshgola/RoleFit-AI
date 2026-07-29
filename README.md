# PlacementPrep AI

An AI-powered agentic application designed to help candidates perform corporate research on target companies, analyze interview formats/rounds, map their skill gaps, and generate customized day-by-day preparation plans. Built with LangChain, Streamlit, and Google Gemini API.

## Architecture Diagram

```text
                  +----------------------------------------------+
                  |               Streamlit Dashboard            |
                  |                   (app.py)                   |
                  +-------+------------------------------+-------+
                          |                              ^
        1. User Inputs    |                              |  5. Renders Prep Report
       (Company, Resume,  v                              |     & raw data tabs
        Job Description)  +------------------------------+-------+
                          |        Orchestration Pipeline        |
                          |             (pipeline.py)            |
                          +-------+----------------------+-------+
                                  |                      |
            2. Run Agents         |                      | 4. Compile Report
                                  v                      v
                +-----------------+--+        +----------+-----------+
                |    LangChain Agents|        |   LangChain Chains   |
                |    (agents.py)     |        |     (agents.py)      |
                +----+---------------+        +----+-----------------+
                | - CompanyResearch  |        | - skill_gap_chain    |
                | - InterviewPattern |        | - report_writer_chain|
                +----+---------------+        +----------------------+
                     |
        3. Web tools |
                     v
                +----+---------------+
                |  Pipeline Tools    |
                |    (tools.py)      |
                +--------------------+
                | - web_search       |
                | - scrape_url       |
                | - parse_resume     |
                +--------------------+
```

## Features

- **Company Intelligence**: Searches the web to identify core business domains, news, and organizational values.
- **Interview Mining**: Evaluates typical interview stages and pulls likely questions from community forums (Glassdoor, Reddit, LeetCode Discuss style sources).
- **Skill Gap Analysis**: Compares a PDF resume directly against a job description, outputting matching skills, critical gap areas, and Estimated Readiness scores.
- **Unified Prep Report**: Compiles all findings into a structured day-by-day 2-week preparation calendar with pre-interview checklists.

## Setup Instructions

### 1. Clone or Download the Project
Ensure you are inside the project root directory `AI-RESEARCHER`.

### 2. Create and Activate a Virtual Environment
Set up a clean environment to install dependencies:

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
Install all required libraries inside the virtual environment:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Duplicate `.env.example` and name the file `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your credentials:
```env
GEMINI_API_KEY=your-gemini-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
```

## Running the Application

### Running the Web Interface (Streamlit)
To launch the dashboard interface:
```bash
streamlit run app.py
```

### Running the Command Line Interface (CLI Test)
You can also run the pipeline end-to-end via CLI for testing:
```bash
python pipeline.py
```

> [!NOTE]
> **Rate Limit Safeguards & Quota Warnings**:
> - **Gemini free tier**: check current RPM/RPD limits at ai.google.dev before a live demo.
> - **Tavily free tier**: 1000 searches/month — each analysis run uses ~2-3 searches.


## Streamlit Community Cloud Deployment

To deploy this application on [Streamlit Community Cloud](https://streamlit.io/cloud):
1. Push the code to a public GitHub repository (ensuring `.env` is ignored by `.gitignore`).
2. Connect your repo to Streamlit Cloud.
3. Open **Advanced Settings** -> **Secrets** in the Streamlit Cloud dashboard and add the following keys:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
TAVILY_API_KEY = "your-tavily-api-key"
```

## Sample Screenshot

![Dashboard Screenshot Placeholder](https://raw.githubusercontent.com/streamlit/streamlit/main/examples/assets/streamlit-logo.png)
