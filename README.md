## PROJECT 2 — Recruitment Analyst Multi-Agent System (Analyzes resumes, matches skills with JD & Generates Interview Questions)

## Short Description:
AI-powered recruitment pipeline where 3 collaborative agents analyse resumes, match skills according to JDs, and generate tailored interview questions through shared memory architecture.

## Full GitHub Repository Description

### 🧑‍💼 Recruitment Analyst Multi-Agent System — Collaborative AI for Hiring Intelligence

A production-grade multi-agent AI system where three specialist agents collaborate through a **shared memory architecture** to deliver end-to-end recruitment analysis: structured resume parsing, JD skills matching with a 0–100 score, and a 14-question tailored interview set — all synthesised into a final hiring report.

#### 🔑 What makes this unique:

**Shared Memory Collaboration — Agents That Build On Each Other**
The core design principle: each agent reads the structured output of the previous agent rather than re-processing raw inputs. The Resume Analyzer extracts a rich JSON profile from the resume. The Skills Matcher reads that structured profile directly — it never sees raw text. The Interview Generator reads both prior outputs, using identified skill gaps to generate harder technical questions on exactly the areas the candidate is weakest in. This is how the system achieves coherent, non-redundant, increasingly intelligent output at each stage.

**SharedMemory as the System's Central Nervous System**
A typed Python `@dataclass` acts as the shared context store. Every read and write is logged with a timestamp. `is_complete()` guards prevent downstream agents from running on incomplete context. The memory object can be serialised to JSON for persistent cross-session storage or audit purposes.

**Full Resume Format Support**
Accepts resumes and job descriptions in `.txt`, `.pdf`, or `.docx` format. The `P2_file_reader.py` utility auto-detects format and routes to the appropriate parser (PyPDF2, python-docx, or pathlib) — real-world ready.

**Structured JSON Throughout**
All three specialist agents use GPT-4o-mini's `response_format: json_object` mode. Every output is guaranteed-parseable structured data — no regex, no fragile string parsing. The orchestrator assembles a rich result bundle combining all structured outputs with a narrative synthesis.

**14-Question Tailored Interview Set**
The Interview Generator doesn't produce generic questions. It reads the specific skill gaps identified by the matcher and generates harder questions on those exact topics. Questions span 5 categories: Behavioural (STAR), Technical, Scenario, Culture-fit, and Closing — each with `what_to_look_for` interviewer guidance.

#### 🏗️ Architecture:
```
Resume + JD
    ↓
SharedMemory
    ↓
ResumeAnalyzer → SkillsMatcher → InterviewGenerator → Orchestrator
    ↓                ↓                ↓                    ↓
resume_profile   skills_match    interview_qs         final_report
    ↓────────────────↓────────────────↓────────────────────↓
                              Full Report Bundle
```

#### 🛠️ Tech Stack:
Python · OpenAI GPT-4o-mini · PyPDF2 · python-docx · sentence-transformers · ChromaDB · Rich

#### 📁 Key Files:
| File | Role |
|------|------|
| `P2_memory.py` | SharedMemory — the collaboration backbone |
| `P2_resume_analyzer.py` | Agent 1: resume → structured JSON profile |
| `P2_skills_matcher.py` | Agent 2: skills vs JD → match score + gaps |
| `P2_interview_generator.py` | Agent 3: 14 tailored interview questions |
| `P2_orchestrator.py` | Pipeline coordinator + final report writer |
| `P2_file_reader.py` | Multi-format file reader (.txt/.pdf/.docx) |
| `P2_settings.py` | All 4 agent system prompts + config |
| `P2_main.py` | CLI entry point with file args + JSON output |

#### 🚀 Quick Start:
```bash
pip install -r P2_requirements.txt
In Env file
Open_API_Key = "Your Open API Key here"
model="gpt-4o-mini"

python P2_main.py                                      # sample data
python P2_main.py --resume resume.pdf --jd jd.txt      # custom files
python P2_main.py --output report.json                 # save JSON
```

#### 📊 Output Includes:
- ✅ Structured candidate profile (name, skills, experience, education, certs)
- ✅ Required skills match table (YES / PARTIAL / NO per skill, with evidence)
- ✅ Nice-to-have skills match
- ✅ Overall match score (0–100)
- ✅ Key skill gaps list
- ✅ Hire recommendation (STRONG YES / YES / MAYBE / NO)
- ✅ 14 tailored interview questions with difficulty ratings + interviewer guidance
- ✅ 5-section narrative recruitment report
- ✅ Full agent activity log with timestamps

#### 💡 Use Cases:
- Automate initial resume screening
- Standardise skills-gap analysis across hiring teams
- Generate consistent interview question sets for different candidates
- Produce sharable hiring reports for stakeholders
- Portfolio project demonstrating multi-agent AI architecture

#### 🔧 Extend It:
- Add a **ScoreboardAgent** that ranks multiple candidates against the same JD
- Swap SharedMemory in-memory dict for **Redis** to persist across sessions
- Add a **Streamlit UI** over `P2_orchestrator.py` for a recruiter dashboard
- Integrate with **LinkedIn API** to pull resume data directly

Topics can be added in future enhancement
multi-agent-ai  langchain  openai  faiss  vector-search  rag
recruitment-automation  nlp  python  gpt4  sentence-transformers
ai-agents  orchestration  enterprise-ai  data-engineering

<img width="1418" height="655" alt="image" src="https://github.com/user-attachments/assets/f743218c-5d7c-44cb-aa9c-944b8fb05cb9" />

<img width="1442" height="616" alt="image" src="https://github.com/user-attachments/assets/5a43868a-7237-44a1-942b-b3ca13260901" />

<img width="1473" height="578" alt="image" src="https://github.com/user-attachments/assets/bd7da3f3-af1e-45ad-92ca-cd1770a146bc" />

<img width="1397" height="591" alt="image" src="https://github.com/user-attachments/assets/1ff88c1e-ec7e-40cc-a3b6-eace68e5caeb" />

<img width="1392" height="582" alt="image" src="https://github.com/user-attachments/assets/6a1adcb6-9a64-4e7e-8a56-c4d04aaf4a6c" />

<img width="1325" height="576" alt="image" src="https://github.com/user-attachments/assets/cfb9c3e6-b193-4936-99e8-bcd37a4b6281" />

<img width="1251" height="602" alt="image" src="https://github.com/user-attachments/assets/931def0f-a2c3-4ed9-bc3a-3c1bec0810eb" />

<img width="1563" height="425" alt="image" src="https://github.com/user-attachments/assets/b8fee8d8-4b49-41f8-b3de-a46c06ba63f2" />

