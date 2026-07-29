# RoleFit AI
> **AI-Powered Multi-Agent Placement Research Assistant**

RoleFit AI is an agentic application designed to help job candidates perform automated company research, analyze interview questions/rounds, map their specific resume skill gaps against job descriptions, and generate customized preparation reports. Built with LangChain, Streamlit, and Google Gemini API.

---

## 📸 Application Screenshot

![RoleFit AI Dashboard](screenshot.png)

---

## 💡 Why This Project?

Unlike generic trivia-search tools, **RoleFit AI places the candidate's custom background at the center of the preparation pipeline.**

By executing a specialized **Resume-JD Skill Gap Analysis**, the system:
1. Performs a line-by-line comparison of candidate projects and tools against specific technical requirements in the Job Description.
2. Formulates an **Estimated Readiness Score** based on direct stack overlap.
3. Automatically adapts a **14-day study plan** focusing exclusively on bridging identified gaps (e.g., PostgreSQL DB connectivity, distributed transactions, scale systems).
4. Highlights the skill gap analysis in a prominent visual container inside the dashboard.

---

## 🏗️ Architecture Diagram

```text
                  +----------------------------------------------+
                  |              Streamlit Dashboard             |
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

---

## 🛠️ Setup & Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/dakshgola/RoleFit-AI.git
cd RoleFit-AI
```

### 2. Create and Activate Virtual Environment

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

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your-gemini-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
```

### 5. Launch the Streamlit App
To launch the Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

> [!NOTE]
> **API limits and safeguards**:
> - **Gemini free tier**: check current RPM/RPD limits at ai.google.dev before running a live demo.
> - **Tavily free tier**: 1000 searches/month — each analysis run uses ~2-3 searches.
