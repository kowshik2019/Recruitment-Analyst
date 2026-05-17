"""
agents/interview_generator.py
-----------------------------
InterviewGeneratorAgent — Agent 3 in the Recruitment Analyst pipeline.

Responsibility:
  Generate a tailored, structured interview question set based on:
    - The candidate's profile (skills, experience, gaps)
    - The job description
    - The skills match analysis (including gaps to probe)

Memory interaction:
  READS : memory.resume_profile   (from Agent 1)
  READS : memory.raw_jd_text      (original JD)
  READS : memory.skills_match     (from Agent 2 — used to focus questions on gaps)
  WRITES: memory.interview_qs     (via memory.set_interview_questions)

Question categories generated:
  - Behavioural  (STAR format)
  - Technical    (JD skill-based)
  - Scenario     (role-specific situation handling)
  - Culture-fit  (motivation, values alignment)
  - Closing      (candidate questions, role clarity)
"""

from __future__ import annotations

import json
from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, INTERVIEW_GENERATOR_PROMPT
from utils.memory    import SharedMemory


class InterviewGeneratorAgent:
    """Generates tailored interview questions using full shared context."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("[InterviewGeneratorAgent] Initialised.")

    def run(self, memory: SharedMemory) -> dict:
        """
        Generate interview questions from shared memory context.

        Parameters
        ----------
        memory : SharedMemory instance

        Returns
        -------
        dict  — structured interview question set
        """
        if not memory.resume_profile:
            raise ValueError("[InterviewGeneratorAgent] Resume profile missing.")
        if not memory.skills_match:
            raise ValueError("[InterviewGeneratorAgent] Skills match missing — run SkillsMatcherAgent first.")

        print("[InterviewGeneratorAgent] Generating interview questions …")

        user_content = (
            f"CANDIDATE PROFILE:\n{json.dumps(memory.resume_profile, indent=2)}\n\n"
            f"JOB DESCRIPTION:\n{memory.raw_jd_text}\n\n"
            f"SKILLS MATCH ANALYSIS:\n{json.dumps(memory.skills_match, indent=2)}"
        )

        resp = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": INTERVIEW_GENERATOR_PROMPT},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )

        raw = resp.choices[0].message.content
        qs  = self._safe_parse(raw)

        memory.set_interview_questions(qs)
        total = qs.get("total_questions", len(qs.get("questions", [])))
        print(f"[InterviewGeneratorAgent] ✓ Generated {total} interview questions.")
        return qs

    @staticmethod
    def _safe_parse(text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "total_questions": 0,
                "questions": [],
                "error": "Failed to parse JSON",
            }
