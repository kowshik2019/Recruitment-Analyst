# 🧑‍💼 Recruitment Analyst Multi-Agent System
### Collaborative AI Pipeline for Resume Analysis, Skills Matching & Interview Generation

---

## 📌 What Is This Project?

The **Recruitment Analyst Multi-Agent System** is a collaborative AI pipeline where three specialist agents — **Resume Analyzer**, **Skills Matcher**, and **Interview Question Generator** — work together through a **shared memory** architecture to produce a complete recruitment analysis report from just a resume and a job description.

Each agent builds on the structured output of the previous one. They never repeat work. They communicate through a typed `SharedMemory` dataclass that acts as the central nervous system of the pipeline. An **OrchestratorAgent** coordinates the full flow and synthesises a final 5-section recruitment report.

**Input:** Resume file (`.txt`, `.pdf`, `.docx`) + Job Description file  
**Output:** Match score, hire recommendation, skills gap analysis, 14 tailored interview questions, final narrative report

---

## 🏗️ System Architecture

```
┌──────────────────────────────┐     ┌──────────────────────────────┐
│   Resume File                │     │   Job Description File        │
│   (.txt / .pdf / .docx)      │     │   (.txt / .pdf / .docx)       │
└──────────────┬───────────────┘     └──────────────┬───────────────┘
               │ read_file()                         │ read_file()
               └────────────────┬────────────────────┘
                                │
                                ▼
               ┌────────────────────────────────────┐
               │           SharedMemory              │
               │   session_id: "20250516_143022"     │
               │   raw_resume_text: "..."            │  ← SET BY CALLER
               │   raw_jd_text: "..."               │  ← SET BY CALLER
               │   resume_profile: {}               │  ← EMPTY at start
               │   skills_match: {}                 │  ← EMPTY at start
               │   interview_qs: {}                 │  ← EMPTY at start
               │   final_report: ""                 │  ← EMPTY at start
               │   agent_log: []                    │
               └────────────────────────────────────┘
                                │
          ┌─────────────────────┼────────────────────────┐
          │                     │                        │
          ▼                     │                        │
┌──────────────────────┐        │                        │
│  AGENT 1             │        │                        │
│  ResumeAnalyzer      │        │                        │
│                      │        │                        │
│  READS:              │        │                        │
│  raw_resume_text     │        │                        │
│                      │        │                        │
│  WRITES:             │        │                        │
│  resume_profile ─────┼────────┼──────────────────────┐ │
│  {name, skills,      │        │                      │ │
│   experience,        │        │                      │ │
│   education...}      │        │                      │ │
└──────────────────────┘        │                      │ │
                                ▼                      │ │
                   ┌──────────────────────┐            │ │
                   │  AGENT 2             │            │ │
                   │  SkillsMatcher       │            │ │
                   │                      │            │ │
                   │  READS:              │            │ │
                   │  resume_profile ◄────┼────────────┘ │
                   │  raw_jd_text         │              │
                   │                      │              │
                   │  WRITES:             │              │
                   │  skills_match ───────┼──────────────┼──┐
                   │  {score:82%,         │              │  │
                   │   gaps:[...],        │              │  │
                   │   recommendation}    │              │  │
                   └──────────────────────┘              │  │
                                                         │  │
                                          ┌──────────────▼──▼──────────┐
                                          │  AGENT 3                    │
                                          │  InterviewGenerator         │
                                          │                             │
                                          │  READS:                     │
                                          │  resume_profile ◄──────────┘
                                          │  raw_jd_text                │
                                          │  skills_match ◄─────────────┘
                                          │                             │
                                          │  WRITES:                    │
                                          │  interview_qs               │
                                          │  {14 tailored questions}    │
                                          └──────────────┬──────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │  ORCHESTRATOR                │
                                          │  Reads ALL memory outputs    │
                                          │  Writes: final_report        │
                                          │  (5-section narrative)       │
                                          └──────────────┬───────────────┘
                                                         │
                                                         ▼
                                               COMPLETE REPORT OUTPUT
                                          (console + optional JSON file)
```

---

## 📁 File Structure & Descriptions

```
Project2_Recruitment_Analyst/
│
├── P2_main.py                  ← Entry point. Loads files, runs pipeline, prints report.
├── P2_settings.py              ← All config: API keys, all 4 agent system prompts.
├── P2_memory.py                ← SharedMemory dataclass — backbone of agent collaboration.
├── P2_file_reader.py           ← Read .txt, .pdf, .docx files into plain text.
├── P2_resume_analyzer.py       ← Agent 1: extracts structured profile from raw resume.
├── P2_skills_matcher.py        ← Agent 2: matches candidate skills against JD.
├── P2_interview_generator.py   ← Agent 3: generates 14 tailored interview questions.
├── P2_orchestrator.py          ← Pipeline coordinator + final report synthesiser.
├── P2_report_printer.py        ← Rich-based console output for full report.
├── P2_requirements.txt         ← All Python dependencies.
├── P2_sample_resume.txt        ← Example: 6-year Data Engineer resume.
├── P2_sample_jd.txt            ← Example: Senior Data Engineer JD.
└── P2_README.md                ← This file.
```

### Detailed File Explanations

#### `P2_main.py` — Entry Point
The application entry point. Three run modes:
- **Demo mode** (no args): Uses bundled `P2_sample_resume.txt` + `P2_sample_jd.txt`
- **Custom files**: `python P2_main.py --resume my_cv.pdf --jd job.txt`
- **Save JSON**: `python P2_main.py --output report.json` — dumps full result to file

Calls `read_file()` to load inputs, instantiates `OrchestratorAgent`, runs `analyse()`, then calls `print_full_report()` for console display.

#### `P2_settings.py` — Configuration Hub
Central config. Everything lives here:
- OpenAI API key and model (from `.env`)
- Embedding model + ChromaDB path
- `RESUME_ANALYZER_PROMPT` — instructs LLM to extract structured JSON with name, skills, work history, education, certifications, summary
- `SKILL_MATCHER_PROMPT` — instructs LLM to compare skills vs JD required/nice-to-have, produce score 0-100, gaps, hire recommendation
- `INTERVIEW_GENERATOR_PROMPT` — instructs LLM to produce 14 categorised questions with `what_to_look_for` pointers per question
- `ORCHESTRATOR_PROMPT` — instructs LLM to synthesise a 5-section narrative report

#### `P2_memory.py` — SharedMemory (The Collaboration Backbone)
This is the most critical design component. A Python `@dataclass` with typed fields:

```python
@dataclass
class SharedMemory:
    session_id:       str   # unique per run
    raw_resume_text:  str   # set by caller
    raw_jd_text:      str   # set by caller
    resume_profile:   dict  # written by ResumeAnalyzerAgent
    skills_match:     dict  # written by SkillsMatcherAgent
    interview_qs:     dict  # written by InterviewGeneratorAgent
    final_report:     str   # written by OrchestratorAgent
    agent_log:        list  # timestamped activity trail
```

Key methods:
- `set_resume_profile()`, `set_skills_match()`, `set_interview_questions()`, `set_final_report()` — typed write methods with automatic logging
- `get_candidate_name()`, `get_skills()`, `get_match_score()` — convenience readers
- `is_complete()` — True when all 3 specialist agents have written their output
- `summary()` — one-liner session status string

Every agent read/write is logged to `agent_log` with timestamp → full audit trail.

#### `P2_file_reader.py` — Multi-Format File Reader
Detects file type by extension and routes to the correct parser:
- `.txt` → `pathlib.Path.read_text()`
- `.pdf` → `PyPDF2.PdfReader` (extracts text from all pages)
- `.docx` / `.doc` → `python-docx Document` (extracts all paragraph text)

Returns clean plain text string for downstream agents. Raises clear errors for unsupported formats.

#### `P2_resume_analyzer.py` — Agent 1: Resume Analyzer
First agent in the pipeline. Steps:
1. Reads `memory.raw_resume_text`
2. Calls GPT-4o-mini with `RESUME_ANALYZER_PROMPT` + resume text
3. Uses `response_format: json_object` to guarantee parseable structured output
4. Writes result to `memory.resume_profile`

Output structure:
```json
{
  "candidate_name": "John Smith",
  "total_experience_years": 6,
  "skills": ["Python", "PySpark", "Kafka", "Snowflake", ...],
  "work_history": [{"company": "...", "role": "...", "highlights": [...]}],
  "education": ["M.S. Computer Science — State University"],
  "certifications": ["AWS Data Analytics Specialty", "SnowPro Core"],
  "summary": "Experienced Data Engineer with 6 years..."
}
```

#### `P2_skills_matcher.py` — Agent 2: Skills Matcher
Second agent. Never re-reads the raw resume — reads `memory.resume_profile` (already structured). Steps:
1. Reads `memory.resume_profile` + `memory.raw_jd_text`
2. Sends structured profile + JD to GPT-4o-mini with `SKILL_MATCHER_PROMPT`
3. Writes match result to `memory.skills_match`

Output structure:
```json
{
  "required_skills_match": [
    {"skill": "PySpark", "candidate_has": "YES", "evidence": "Built streaming pipelines at TechCorp"}
  ],
  "nice_to_have_match": [...],
  "overall_match_score": 82,
  "key_gaps": ["Terraform", "LangChain", "Fintech domain"],
  "hire_recommendation": "STRONG YES",
  "recommendation_reason": "Strong match on 9/11 required skills..."
}
```

#### `P2_interview_generator.py` — Agent 3: Interview Generator
Third agent. Reads ALL prior outputs — most information-rich agent in the pipeline. Uses skill gaps from Agent 2 to focus difficult questions. Steps:
1. Reads `memory.resume_profile` + `memory.raw_jd_text` + `memory.skills_match`
2. Calls GPT-4o-mini with `INTERVIEW_GENERATOR_PROMPT`
3. Writes to `memory.interview_qs`

Generates 14 questions across 5 categories:
- 3 Behavioural (STAR format)
- 5 Technical (JD skill-targeted, harder on identified gaps)
- 3 Scenario (role-specific situation handling)
- 2 Culture-fit / motivation
- 1 Closing

Each question includes: `question_text`, `category`, `difficulty` (easy/medium/hard), `what_to_look_for` (ideal answer pointers for the interviewer).

#### `P2_orchestrator.py` — Pipeline Coordinator
The only class `P2_main.py` interacts with. Steps:
1. Initialises `SharedMemory`
2. Runs Agent 1 → Agent 2 → Agent 3 in sequence
3. Calls `_generate_report()` — sends all structured memory to GPT-4o-mini for synthesis
4. Writes final report to `memory.final_report`
5. Returns complete result bundle: all structured data + narrative report + agent log

#### `P2_report_printer.py` — Rich Console Output
Pretty-prints the full result using `rich`:
- Session header with candidate name, match score (colour-coded), recommendation
- Required skills match table (YES=green, PARTIAL=yellow, NO=red)
- Key gaps panel (red border)
- Interview questions table with difficulty colour coding
- Final report in full-width panel

---

## 🔄 Data Flow — Step by Step

```
1. Call: orchestrator.analyse(resume_text, jd_text)

2. SharedMemory created:
   memory.raw_resume_text = resume_text
   memory.raw_jd_text = jd_text

3. ResumeAnalyzerAgent.run(memory):
   → LLM extracts structured profile
   → memory.resume_profile = {name, skills:[14 skills], experience:6, ...}
   → agent_log: [{agent:"ResumeAnalyzer", action:"Wrote resume_profile", ts:...}]

4. SkillsMatcherAgent.run(memory):
   → Reads memory.resume_profile (structured — no re-parsing)
   → LLM matches 11 required skills, 5 nice-to-have
   → memory.skills_match = {score:82, gaps:["Terraform","LangChain"], rec:"STRONG YES"}
   → agent_log: +1 entry

5. InterviewGeneratorAgent.run(memory):
   → Reads profile + JD + match (all 3 prior outputs)
   → LLM generates 14 questions, targeting gaps on hard difficulty
   → memory.interview_qs = {total_questions:14, questions:[...]}
   → agent_log: +1 entry

6. OrchestratorAgent._generate_report(memory):
   → Sends all structured data to LLM
   → Returns 5-section markdown narrative
   → memory.final_report = "## Executive Summary\n..."

7. Result bundle returned. print_full_report() renders to console.
```

---

## ⚙️ Setup & Execution

### Prerequisites
- Python 3.10+
- OpenAI API key

### Step 1 — Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### Step 2 — Install Dependencies
```bash
pip install -r P2_requirements.txt
```

### Step 3 — Configure Environment
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env
echo "VECTOR_DB_PATH=./chroma_store" >> .env
```

### Step 4 — Fix Imports (flat file structure)
Since files are prefixed and flat, update imports in each file:

In `P2_orchestrator.py`:
```python
from config.settings import ...              →  from P2_settings import ...
from agents.resume_analyzer import ...       →  from P2_resume_analyzer import ...
from agents.skills_matcher import ...        →  from P2_skills_matcher import ...
from agents.interview_generator import ...   →  from P2_interview_generator import ...
from utils.memory import ...                 →  from P2_memory import ...
```

In `P2_resume_analyzer.py`, `P2_skills_matcher.py`, `P2_interview_generator.py`:
```python
from config.settings import ...  →  from P2_settings import ...
from utils.memory import ...     →  from P2_memory import ...
```

In `P2_main.py`:
```python
from agents.orchestrator import ...   →  from P2_orchestrator import ...
from utils.file_reader import ...     →  from P2_file_reader import ...
from utils.report_printer import ...  →  from P2_report_printer import ...
```

### Step 5 — Run with Sample Data
```bash
python P2_main.py
```

### Step 6 — Run with Custom Files
```bash
python P2_main.py --resume /path/to/resume.pdf --jd /path/to/jd.txt
```

### Step 7 — Save Full JSON Output
```bash
python P2_main.py --resume resume.pdf --jd jd.txt --output report.json
```

---

## 📊 Sample Output

```
══════════════════ RECRUITMENT ANALYST REPORT ══════════════════
Session    : 20250516_143022
Candidate  : John Smith
Match Score: 82%   ████████░░  STRONG YES

Required Skills Match:
┌──────────────────────┬──────────┬──────────────────────────────────┐
│ Skill                │ Has It?  │ Evidence                         │
├──────────────────────┼──────────┼──────────────────────────────────┤
│ Python               │ YES ✅   │ Primary language, 6 years         │
│ PySpark              │ YES ✅   │ Streaming pipelines at TechCorp   │
│ Snowflake            │ YES ✅   │ SnowPro certified, both companies │
│ Kafka                │ YES ✅   │ 500K events/day pipeline          │
│ Airflow              │ YES ✅   │ MLflow+Airflow integration         │
│ dbt                  │ YES ✅   │ Certified, 5 domain dbt models    │
│ Terraform            │ PARTIAL ⚠️│ "Basics" mentioned only          │
│ LangChain            │ NO ❌    │ Not found in resume               │
└──────────────────────┴──────────┴──────────────────────────────────┘

Key Gaps: Terraform (beyond basics), LangChain, Fintech domain exp.

Interview Questions: 14 generated
#  Category      Difficulty  Question
1  behavioural   medium      Tell me about a time you reduced pipeline latency...
2  technical     hard        Explain how you'd design an exactly-once Kafka pipeline...
3  technical     hard        How would you implement LangChain in a data pipeline?...
...
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `openai` | ≥1.30 | LLM API — all 4 agents |
| `PyPDF2` | ≥3.0 | Extract text from PDF resumes |
| `python-docx` | ≥1.1 | Extract text from Word resumes |
| `sentence-transformers` | ≥3.0 | Embedding (available for extensions) |
| `faiss-cpu` | ≥1.7.4 | Vector similarity (available for extensions) |
| `chromadb` | ≥0.5 | Persistent vector store (available for extensions) |
| `python-dotenv` | ≥1.0 | `.env` loading |
| `rich` | ≥13.7 | Coloured console output |
| `pydantic` | ≥2.7 | Data validation |

---

## 🧠 Key Design Decisions

| Decision | Why |
|---|---|
| SharedMemory dataclass | Clean typed interface. No passing huge raw dicts between agents. |
| Sequential pipeline | Agent 2 needs Agent 1's output. Agent 3 needs both. Order is intentional. |
| JSON-mode LLM responses | All 3 specialist agents return guaranteed-parseable JSON. No regex needed. |
| Agents never re-read raw text | Once Resume Analyzer structures the profile, all other agents use that — efficient. |
| `agent_log` with timestamps | Full audit trail. Know exactly what each agent did and when. |
| Supports PDF/DOCX/TXT | Real-world resumes come in all formats. |
| `is_complete()` guard | Prevents downstream agents from running on incomplete context. |
