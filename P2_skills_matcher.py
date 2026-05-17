"""
agents/skills_matcher.py
------------------------
SkillsMatcherAgent — Agent 2 in the Recruitment Analyst pipeline.

Responsibility:
  Compare candidate skills (from resume profile) against JD requirements.
  Produce a match score, gap analysis, and hiring recommendation.

Memory interaction:
  READS : memory.resume_profile  (written by ResumeAnalyzerAgent)
  READS : memory.raw_jd_text
  WRITES: memory.skills_match    (via memory.set_skills_match)

By reading directly from SharedMemory, this agent never needs to re-parse
the resume — it uses the already-structured data from Agent 1.
"""

from __future__ import annotations

import json
from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, SKILL_MATCHER_PROMPT
from utils.memory    import SharedMemory


class SkillsMatcherAgent:
    """Matches candidate profile skills against a job description."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("[SkillsMatcherAgent] Initialised.")

    def run(self, memory: SharedMemory) -> dict:
        """
        Run skills matching using data already in shared memory.

        Parameters
        ----------
        memory : SharedMemory instance

        Returns
        -------
        dict  — skills match report
        """
        if not memory.resume_profile:
            raise ValueError("[SkillsMatcherAgent] Resume profile missing — run ResumeAnalyzerAgent first.")
        if not memory.raw_jd_text:
            raise ValueError("[SkillsMatcherAgent] No JD text found in shared memory.")

        print("[SkillsMatcherAgent] Matching skills against JD …")

        user_content = (
            f"CANDIDATE PROFILE:\n{json.dumps(memory.resume_profile, indent=2)}\n\n"
            f"JOB DESCRIPTION:\n{memory.raw_jd_text}"
        )

        resp = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SKILL_MATCHER_PROMPT},
                {"role": "user",   "content": user_content},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        raw   = resp.choices[0].message.content
        match = self._safe_parse(raw)

        memory.set_skills_match(match)
        score = match.get("overall_match_score", 0)
        rec   = match.get("hire_recommendation", "UNKNOWN")
        print(f"[SkillsMatcherAgent] ✓ Match score: {score}% | Recommendation: {rec}")
        return match

    @staticmethod
    def _safe_parse(text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "overall_match_score": 0,
                "hire_recommendation": "UNKNOWN",
                "error": "Failed to parse JSON",
            }
