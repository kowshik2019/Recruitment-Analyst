"""
main.py
-------
Entry point for the Recruitment Analyst Multi-Agent System.

Usage modes:
  1. Demo mode (default):
       python main.py
       → Uses bundled sample resume + JD from sample_data/

  2. Custom file mode:
       python main.py --resume path/to/resume.pdf --jd path/to/jd.txt

  3. Save output:
       python main.py --output report.json
       → Saves full JSON result to file in addition to console output

Supported file types: .txt, .pdf, .docx
"""

import sys
import json
import argparse
from pathlib    import Path
from rich.console import Console

from agents.orchestrator  import OrchestratorAgent
from utils.file_reader    import read_file
from utils.report_printer import print_full_report

console = Console()

SAMPLE_RESUME = "sample_data/sample_resume.txt"
SAMPLE_JD     = "sample_data/sample_jd.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recruitment Analyst Multi-Agent System"
    )
    parser.add_argument("--resume", default=SAMPLE_RESUME,
                        help="Path to resume file (.txt, .pdf, .docx)")
    parser.add_argument("--jd",     default=SAMPLE_JD,
                        help="Path to job description file (.txt, .pdf, .docx)")
    parser.add_argument("--output", default=None,
                        help="Optional: path to save JSON output (e.g. report.json)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Load files ─────────────────────────────────────────────────────────────
    console.print(f"\n[cyan]Loading resume:[/cyan]  {args.resume}")
    resume_text = read_file(args.resume)

    console.print(f"[cyan]Loading JD:[/cyan]      {args.jd}\n")
    jd_text = read_file(args.jd)

    # ── Run pipeline ──────────────────────────────────────────────────────────
    orchestrator = OrchestratorAgent()
    result       = orchestrator.analyse(resume_text, jd_text)

    # ── Print report ──────────────────────────────────────────────────────────
    print_full_report(result)

    # ── Optionally save JSON output ───────────────────────────────────────────
    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[green]✓ Full JSON report saved to:[/green] {out_path}")


if __name__ == "__main__":
    main()
