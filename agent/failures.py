"""Step 1 of the agent: read failed tests out of reports/results.xml.

No AI here. These plain functions become the agent's tools in the next step.
Run it:  python -m agent.failures
"""
import ast
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_XML = ROOT / "reports" / "results.xml"


def list_failures(xml_path: Path = RESULTS_XML) -> list[dict]:
    """Return one dict per failed or errored test."""
    if not xml_path.exists():
        raise FileNotFoundError(f"{xml_path} not found. Run pytest first.")

    failures = []
    for case in ET.parse(xml_path).getroot().iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is None:
            continue

        props = {p.get("name"): p.get("value") for p in case.iter("property")}
        failures.append({
            "test_id": f"{case.get('classname')}.{case.get('name')}",
            "file": case.get("classname").replace(".", "/") + ".py",
            "node_id": case.get("classname").replace(".", "/") + ".py::" + case.get("name"),
            "function": case.get("name").split("[")[0],
            "message": problem.get("message", "").split("\n")[0],
            "traceback": (problem.text or "").strip(),
            "screenshot": props.get("playwright_screenshot"),
            "trace": props.get("playwright_trace"),
        })
    return failures


def get_test_source(file: str, function: str) -> str:
    """Return the source code of one test function."""
    path = ROOT / file
    if not path.exists():
        return ""
    source = path.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            return ast.get_source_segment(source, node) or ""
    return ""


def get_failure_details(test_id: str) -> dict:
    """Everything known about one failure, including the test's source code."""
    for failure in list_failures():
        if failure["test_id"] == test_id:
            return {**failure, "source": get_test_source(failure["file"], failure["function"])}
    return {"error": f"No failure found with test_id '{test_id}'"}


if __name__ == "__main__":
    found = list_failures()
    print(f"{len(found)} failed test(s)\n")
    for f in found:
        print(f["test_id"])
        print(f"  message:    {f['message']}")
        print(f"  screenshot: {f['screenshot']}")
        print(f"  source:     {len(get_test_source(f['file'], f['function']).splitlines())} lines\n")
