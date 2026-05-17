"""
agents/resume_analyzer.py
-------------------------
ResumeAnalyzerAgent — Agent 1 in the Recruitment Analyst pipeline.

Responsibility:
  Parse raw resume text → return a rich structured JSON profile.

Memory interaction:
  READS : memory.raw_resume_text
  WRITES: memory.resume_profile  (via memory.set_resume_profile)

The structured profile is then shared with SkillsMatcherAgent and
InterviewGeneratorAgent via SharedMemory — no re-processing needed.
"""

from __future__ import annotations

import json
from openai import OpenAI

from config.settings    import OPENAI_API_KEY, OPENAI_MODEL, RESUME_ANALYZER_PROMPT
from utils.memory       import SharedMemory


class ResumeAnalyzerAgent:
    """Extracts structured candidate data from raw resume text."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("[ResumeAnalyzerAgent] Initialised.")

    def run(self, memory: SharedMemory) -> dict:
        """
        Parse resume from shared memory and write structured profile back.

        Parameters
        ----------
        memory : SharedMemory instance (shared across all agents)

        Returns
        -------
        dict  — structured resume profile
        """
        if not memory.raw_resume_text:
            raise ValueError("[ResumeAnalyzerAgent] No resume text found in shared memory.")

        print("[ResumeAnalyzerAgent] Analysing resume …")

        resp = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": RESUME_ANALYZER_PROMPT},
                {"role": "user",   "content": f"RESUME:\n{memory.raw_resume_text}"},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        raw  = resp.choices[0].message.content
        profile = self._safe_parse(raw)

        # Write to shared memory so other agents can use it
        memory.set_resume_profile(profile)
        print(f"[ResumeAnalyzerAgent] ✓ Extracted profile for: {profile.get('candidate_name', 'Unknown')}")
        return profile

    @staticmethod
    def _safe_parse(text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "candidate_name": "Parse Error",
                "skills": [],
                "summary": text[:500],
                "error": "Failed to parse JSON from LLM response",
            }
