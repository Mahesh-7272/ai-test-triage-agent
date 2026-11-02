"""Step 2 of the agent: the actions it can take.

Step 3 hands these functions to Claude as tools.
Try the rerun tool:  python -m agent.tools
"""
import subprocess
import sys

from agent.bug_tracker import BUGS_DIR, ROOT, create_bug, search_existing_bugs  # noqa: F401  (re-exported)
from agent.failures import get_failure_details, list_failures  # noqa: F401  (re-exported)


def rerun_test(node_id: str, times: int = 3) -> dict:
    """Run one test again a few times to see whether the failure is consistent.

    Fails every time -> likely a real bug. Passes sometimes -> likely flaky.
    Reports go to reports/rerun/ so the original results.xml is not overwritten.
    """
    times = max(1, min(times, 5))
    outcomes = []
    for _ in range(times):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", node_id, "-q", "-p", "no:cacheprovider",
             "--junitxml=reports/rerun/results.xml", "--html=reports/rerun/report.html",
             "--output", "reports/rerun/artifacts"],
            cwd=ROOT, capture_output=True, text=True,
        )
        outcomes.append("passed" if result.returncode == 0 else "failed")

    passed = outcomes.count("passed")
    if passed == 0:
        verdict = "consistent_failure"
    elif passed == times:
        verdict = "now_passes"
    else:
        verdict = "flaky"
    return {"node_id": node_id, "runs": outcomes, "verdict": verdict}


def write_summary(markdown: str) -> dict:
    """Save the final triage report to bugs/triage_summary.md."""
    BUGS_DIR.mkdir(parents=True, exist_ok=True)
    path = BUGS_DIR / "triage_summary.md"
    path.write_text(markdown.strip() + "\n", encoding="utf-8")
    return {"saved": str(path.relative_to(ROOT))}


if __name__ == "__main__":
    failures = list_failures()
    if not failures:
        print("No failures to rerun.")
    else:
        first = failures[0]
        print(f"Rerunning twice: {first['node_id']}")
        print(rerun_test(first["node_id"], times=2))
