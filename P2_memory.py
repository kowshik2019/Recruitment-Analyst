"""
utils/memory.py
---------------
SharedMemory — the collaborative context store for the Recruitment Analyst system.

All three specialist agents READ FROM and WRITE TO this shared object.
This allows agents to:
  - Know what previous agents have already computed (avoid redundant work).
  - Build on each other's outputs without re-processing raw inputs.
  - Pass rich structured data between pipeline stages.

Design: simple in-memory dict with typed accessors.
         Can be extended to Redis/ChromaDB for persistence across sessions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SharedMemory:
    """
    Central shared context store for all agents in a single recruitment session.

    Attributes
    ----------
    session_id       : unique ID for this recruitment analysis run
    raw_resume_text  : original resume string (set by caller)
    raw_jd_text      : original job description string (set by caller)
    resume_profile   : structured dict output from ResumeAnalyzerAgent
    skills_match     : structured dict output from SkillsMatcherAgent
    interview_qs     : structured dict output from InterviewGeneratorAgent
    final_report     : markdown string output from OrchestratorAgent
    agent_log        : ordered list of agent activity records
    """

    session_id      : str        = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    raw_resume_text : str        = ""
    raw_jd_text     : str        = ""
    resume_profile  : dict       = field(default_factory=dict)
    skills_match    : dict       = field(default_factory=dict)
    interview_qs    : dict       = field(default_factory=dict)
    final_report    : str        = ""
    agent_log       : list[dict] = field(default_factory=list)

    # ── Agent write methods ───────────────────────────────────────────────────

    def set_resume_profile(self, profile: dict, agent_name: str = "ResumeAnalyzer") -> None:
        self.resume_profile = profile
        self._log(agent_name, "Wrote resume_profile", {"keys": list(profile.keys())})

    def set_skills_match(self, match: dict, agent_name: str = "SkillsMatcher") -> None:
        self.skills_match = match
        self._log(agent_name, "Wrote skills_match",
                  {"score": match.get("overall_match_score"),
                   "recommendation": match.get("hire_recommendation")})

    def set_interview_questions(self, qs: dict, agent_name: str = "InterviewGen") -> None:
        self.interview_qs = qs
        self._log(agent_name, "Wrote interview_qs",
                  {"total_questions": qs.get("total_questions")})

    def set_final_report(self, report: str, agent_name: str = "Orchestrator") -> None:
        self.final_report = report
        self._log(agent_name, "Wrote final_report", {"chars": len(report)})

    # ── Agent read helpers ────────────────────────────────────────────────────

    def get_candidate_name(self) -> str:
        return self.resume_profile.get("candidate_name", "Unknown Candidate")

    def get_skills(self) -> list[str]:
        return self.resume_profile.get("skills", [])

    def get_match_score(self) -> int:
        return self.skills_match.get("overall_match_score", 0)

    def is_complete(self) -> bool:
        """Returns True when all three specialist agents have written their output."""
        return bool(self.resume_profile and self.skills_match and self.interview_qs)

    # ── Utility ───────────────────────────────────────────────────────────────

    def _log(self, agent: str, action: str, meta: Any = None) -> None:
        self.agent_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent":     agent,
            "action":    action,
            "meta":      meta or {},
        })

    def summary(self) -> str:
        lines = [f"Session: {self.session_id}",
                 f"Candidate: {self.get_candidate_name()}",
                 f"Match Score: {self.get_match_score()}%",
                 f"Agents logged: {len(self.agent_log)} events",
                 f"Report ready: {bool(self.final_report)}"]
        return "\n".join(lines)
