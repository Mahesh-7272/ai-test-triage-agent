"""Step 3 of the agent: the loop that lets Claude choose which tool to use.

Two brains share the same tools:
  run_dry()    scripted stand-in, no API key, for testing the pipeline
  run_claude() the real agent: Claude decides, our code executes
"""
import json
import os

from agent import tools

MODEL = "claude-sonnet-5-5"
MAX_TURNS = 40

SYSTEM_PROMPT = """You are a QA triage agent. Pytest/Playwright UI tests were just run.
Investigate every failed test and decide what it is:
  - app_bug: the application behaves wrongly (fails consistently)
  - test_bug: the test itself is wrong (bad assertion, outdated locator)
  - flaky: passes on some reruns
  - environment: network, timeout or site-availability problem

Process for each failure:
  1. Read the details (error, traceback, test source).
  2. Rerun the test to check consistency.
  3. For app bugs, search existing bugs first; only create a bug if none matches.
  4. Never create a bug for flaky or test_bug failures. Explain them in the summary.
Finish by calling write_summary with a markdown report listing every failure,
its category, and the action taken."""

TOOL_SCHEMAS = [
    {"name": "list_failures",
     "description": "List all failed tests from the latest pytest run (test_id, node_id, message).",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_failure_details",
     "description": "Get traceback, screenshot path and the test's source code for one failure.",
     "input_schema": {"type": "object",
                      "properties": {"test_id": {"type": "string"}},
                      "required": ["test_id"]}},
    {"name": "rerun_test",
     "description": "Rerun one test several times to check if the failure is consistent or flaky.",
     "input_schema": {"type": "object",
                      "properties": {"node_id": {"type": "string"},
                                     "times": {"type": "integer", "description": "1 to 5"}},
                      "required": ["node_id"]}},
    {"name": "search_existing_bugs",
     "description": "Search already-filed bugs for duplicates. Use a specific keyword such as the test function name.",
     "input_schema": {"type": "object",
                      "properties": {"query": {"type": "string"}},
                      "required": ["query"]}},
    {"name": "create_bug",
     "description": "File a bug. The user is asked to approve it first.",
     "input_schema": {"type": "object",
                      "properties": {"title": {"type": "string"},
                                     "body": {"type": "string",
                                              "description": "Markdown: steps, expected vs actual, evidence paths, test node_id"},
                                     "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                     "labels": {"type": "array", "items": {"type": "string"}}},
                      "required": ["title", "body", "severity"]}},
    {"name": "write_summary",
     "description": "Save the final triage report (markdown). Call this last.",
     "input_schema": {"type": "object",
                      "properties": {"markdown": {"type": "string"}},
                      "required": ["markdown"]}},
]

TOOL_FUNCTIONS = {
    "list_failures": tools.list_failures,
    "get_failure_details": tools.get_failure_details,
    "rerun_test": tools.rerun_test,
    "search_existing_bugs": tools.search_existing_bugs,
    "create_bug": tools.create_bug,
    "write_summary": tools.write_summary,
}


def execute_tool(name: str, args: dict, approve) -> dict:
    """Run one tool. Filing a bug needs the user's approval first."""
    if name not in TOOL_FUNCTIONS:
        return {"error": f"unknown tool '{name}'"}
    if name == "create_bug" and not approve(args):
        return {"status": "rejected_by_user", "note": "Do not retry. Mention it in the summary."}
    try:
        return TOOL_FUNCTIONS[name](**args)
    except Exception as exc:  # report to the agent instead of crashing the loop
        return {"error": f"{type(exc).__name__}: {exc}"}


def run_claude(approve) -> None:
    """The real agent loop: Claude asks for tools, we run them, repeat until done."""
    from dotenv import load_dotenv
    load_dotenv(tools.ROOT / ".env")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not found. Add it to .env, or use --dry-run.")
        return

    import anthropic
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": "Triage the latest test run."}]

    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL, max_tokens=4000, system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\nClaude: {block.text.strip()}")

        if response.stop_reason != "tool_use":
            return

        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> {block.name}({json.dumps(block.input)[:100]})")
                output = execute_tool(block.name, block.input, approve)
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(output)})
        messages.append({"role": "user", "content": results})

    print(f"Stopped after {MAX_TURNS} turns without finishing.")


def run_dry(approve) -> None:
    """Scripted stand-in for Claude. It uses the same tools but follows fixed rules,
    so it cannot tell an app bug from a wrong test. Real Claude can."""
    rows = []
    failures = tools.list_failures()
    print(f"Found {len(failures)} failed test(s).")

    for f in failures:
        print(f"\n[{f['function']}]")
        details = tools.get_failure_details(f["test_id"])
        rerun = tools.rerun_test(f["node_id"], times=2)
        print(f"  rerun: {rerun['runs']} -> {rerun['verdict']}")

        if rerun["verdict"] != "consistent_failure":
            rows.append((f["node_id"], "flaky", "no bug filed"))
            continue

        duplicates = tools.search_existing_bugs(f["function"])
        if duplicates:
            print(f"  duplicate of {duplicates[0]['bug_id']}")
            rows.append((f["node_id"], "app_bug (duplicate)", f"already filed as {duplicates[0]['bug_id']}"))
            continue

        args = {
            "title": f"{f['function']} fails: {f['message']}",
            "body": (f"**Test:** `{f['node_id']}`\n\n**Error:** {f['message']}\n\n"
                     f"**Reruns:** {rerun['runs']}\n\n**Screenshot:** {f['screenshot']}\n\n"
                     f"```python\n{details.get('source', '')}\n```"),
            "severity": "medium",
            "labels": ["app-bug", "auto-triage"],
        }
        result = execute_tool("create_bug", args, approve)
        print(f"  create_bug -> {result}")
        action = f"filed {result['bug_id']}" if "bug_id" in result else "bug not filed"
        rows.append((f["node_id"], "app_bug", action))

    lines = ["# Triage summary (dry run)", "",
             "| Test | Category | Action |", "|---|---|---|"]
    lines += [f"| `{t}` | {c} | {a} |" for t, c, a in rows]
    print(f"\n{tools.write_summary(chr(10).join(lines))}")
