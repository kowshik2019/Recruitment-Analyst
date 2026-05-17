"""
agents/orchestrator.py
----------------------
OrchestratorAgent — the pipeline coordinator for the Recruitment Analyst system.

Responsibility:
  1. Initialise SharedMemory for the session.
  2. Run ResumeAnalyzerAgent → SkillsMatcherAgent → InterviewGeneratorAgent in order.
  3. Each agent reads from and writes to SharedMemory, building a richer context.
  4. Synthesise all outputs into a final Recruitment Report via LLM.
  5. Return the complete result bundle.

This is the ONLY class the caller (main.py) interacts with directly.
"""

from __future__ import annotations

import json
from openai import OpenAI

from config.settings           import OPENAI_API_KEY, OPENAI_MODEL, ORCHESTRATOR_PROMPT
from utils.memory              import SharedMemory
from agents.resume_analyzer    import ResumeAnalyzerAgent
from agents.skills_matcher     import SkillsMatcherAgent
from agents.interview_generator import InterviewGeneratorAgent


class OrchestratorAgent:
    """Coordinates all specialist agents and produces the final recruitment report."""

    def __init__(self):
        self.client          = OpenAI(api_key=OPENAI_API_KEY)
        self.resume_agent    = ResumeAnalyzerAgent()
        self.matcher_agent   = SkillsMatcherAgent()
        self.interview_agent = InterviewGeneratorAgent()
        print("[OrchestratorAgent] Pipeline ready. All agents initialised.")

    # ── Public API ─────────────────────────────────────────────────────────────

    def analyse(self, resume_text: str, jd_text: str) -> dict:
        """
        Run the full recruitment analysis pipeline.

        Parameters
        ----------
        resume_text : raw text of candidate's resume
        jd_text     : raw text of the job description

        Returns
        -------
        dict with keys:
            session_id     : unique session identifier
            candidate_name : extracted candidate name
            match_score    : 0-100 skills match score
            recommendation : STRONG YES / YES / MAYBE / NO
            resume_profile : full structured profile dict
            skills_match   : full match analysis dict
            interview_qs   : full interview question set dict
            final_report   : markdown-formatted recruitment report
            agent_log      : list of agent activity events
        """
        # ── Step 0: Initialise shared memory ─────────────────────────────────
        memory = SharedMemory()
        memory.raw_resume_text = resume_text
        memory.raw_jd_text     = jd_text
        print(f"\n[OrchestratorAgent] Session {memory.session_id} started.")

        # ── Step 1: Resume Analysis ───────────────────────────────────────────
        self.resume_agent.run(memory)

        # ── Step 2: Skills Matching ───────────────────────────────────────────
        self.matcher_agent.run(memory)

        # ── Step 3: Interview Question Generation ─────────────────────────────
        self.interview_agent.run(memory)

        # ── Step 4: Synthesise final report ──────────────────────────────────
        final_report = self._generate_report(memory)
        memory.set_final_report(final_report)

        print(f"[OrchestratorAgent] ✓ Session {memory.session_id} complete.")
        print(memory.summary())

        return {
            "session_id":     memory.session_id,
            "candidate_name": memory.get_candidate_name(),
            "match_score":    memory.get_match_score(),
            "recommendation": memory.skills_match.get("hire_recommendation", "UNKNOWN"),
            "resume_profile": memory.resume_profile,
            "skills_match":   memory.skills_match,
            "interview_qs":   memory.interview_qs,
            "final_report":   memory.final_report,
            "agent_log":      memory.agent_log,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _generate_report(self, memory: SharedMemory) -> str:
        """Use LLM to write the final synthesised recruitment report."""
        print("[OrchestratorAgent] Generating final recruitment report …")

        context = (
            f"CANDIDATE PROFILE:\n{json.dumps(memory.resume_profile, indent=2)}\n\n"
            f"JOB DESCRIPTION:\n{memory.raw_jd_text}\n\n"
            f"SKILLS MATCH ANALYSIS:\n{json.dumps(memory.skills_match, indent=2)}\n\n"
            f"INTERVIEW QUESTIONS:\n{json.dumps(memory.interview_qs, indent=2)}"
        )

        resp = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": ORCHESTRATOR_PROMPT},
                {"role": "user",   "content": context},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return resp.choices[0].message.content
