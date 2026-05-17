"""
utils/report_printer.py
-----------------------
Rich-based console printer for Recruitment Analyst outputs.
Renders structured analysis results in a readable, coloured format.
"""

from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich.text    import Text
from rich         import box

console = Console()

SCORE_COLORS = {
    range(80, 101): "bold green",
    range(60, 80):  "green",
    range(40, 60):  "yellow",
    range(0,  40):  "red",
}

REC_COLORS = {
    "STRONG YES": "bold green",
    "YES":        "green",
    "MAYBE":      "yellow",
    "NO":         "bold red",
}


def _score_color(score: int) -> str:
    for r, c in SCORE_COLORS.items():
        if score in r:
            return c
    return "white"


def print_full_report(result: dict) -> None:
    """Print the complete recruitment analysis result."""
    console.rule("[bold cyan]RECRUITMENT ANALYST REPORT[/bold cyan]")

    # ── Session header ────────────────────────────────────────────────────────
    score   = result.get("match_score", 0)
    rec     = result.get("recommendation", "UNKNOWN")
    sc      = _score_color(score)
    rc      = REC_COLORS.get(rec, "white")

    header = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    header.add_column("k", style="bold cyan", width=22)
    header.add_column("v", style="white")
    header.add_row("Session ID",       result.get("session_id", ""))
    header.add_row("Candidate",        result.get("candidate_name", ""))
    header.add_row("Match Score",      f"[{sc}]{score}%[/{sc}]")
    header.add_row("Recommendation",   f"[{rc}]{rec}[/{rc}]")
    console.print(header)

    # ── Skills match table ────────────────────────────────────────────────────
    sm = result.get("skills_match", {})
    required = sm.get("required_skills_match", [])
    if required:
        table = Table(title="Required Skills Match", box=box.ROUNDED)
        table.add_column("Skill",     style="cyan")
        table.add_column("Has It?",   style="white", width=10)
        table.add_column("Evidence",  style="dim white")
        for row in required:
            ch = row.get("candidate_has", "NO")
            color = {"YES": "green", "PARTIAL": "yellow", "NO": "red"}.get(ch, "white")
            table.add_row(row.get("skill", ""), f"[{color}]{ch}[/{color}]",
                          row.get("evidence", "")[:60])
        console.print(table)

    # ── Key gaps ──────────────────────────────────────────────────────────────
    gaps = sm.get("key_gaps", [])
    if gaps:
        console.print(Panel(
            "\n".join(f"• {g}" for g in gaps),
            title="[red]Key Gaps[/red]", border_style="red",
        ))

    # ── Interview questions summary ───────────────────────────────────────────
    iq = result.get("interview_qs", {})
    questions = iq.get("questions", [])
    if questions:
        q_table = Table(title=f"Interview Questions ({len(questions)} total)", box=box.ROUNDED)
        q_table.add_column("#",          width=4)
        q_table.add_column("Category",   style="cyan", width=14)
        q_table.add_column("Difficulty", width=10)
        q_table.add_column("Question",   style="white")
        for i, q in enumerate(questions, 1):
            diff  = q.get("difficulty", "medium")
            dc    = {"easy": "green", "medium": "yellow", "hard": "red"}.get(diff, "white")
            q_table.add_row(
                str(i),
                q.get("category", ""),
                f"[{dc}]{diff}[/{dc}]",
                q.get("question_text", "")[:80],
            )
        console.print(q_table)

    # ── Final report ──────────────────────────────────────────────────────────
    if result.get("final_report"):
        console.print(Panel(
            result["final_report"],
            title="[bold cyan]Final Recruitment Report[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        ))

    console.rule("[dim]End of Report[/dim]")
