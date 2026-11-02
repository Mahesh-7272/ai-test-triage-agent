# AI Failure Analyzer: Stage 1 (Playwright + Pytest, Page Object Model)

Practice site: https://www.saucedemo.com

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

## Run
```bash
pytest --headed --slowmo 500          # watch the browser
pytest                                # headless, all tests
pytest -m smoke                       # smoke tests only
pytest -m "not demo_failure"          # skip the tests that fail on purpose
```

Reports and failure evidence land in `reports/`:
`report.html`, `results.xml`, and `artifacts/` (screenshots + traces).
View a trace with `playwright show-trace <path to trace.zip>`.

## Structure
```
pages/       Page Objects: locators + actions, one class per page
tests/       Test cases; they call page objects, never raw locators
utils/       Test data
conftest.py  Fixtures (page objects, logged-in sessions)
pytest.ini   Pytest + Playwright settings
```

## Triage agent
```bash
pytest                                  # creates reports/results.xml
python -m agent.failures                # list the failed tests
python -m agent.tools                   # rerun the first failure twice
python -m agent.main --dry-run          # scripted agent, no API key, asks before filing bugs
python -m agent.main --dry-run --yes    # same, approve every bug automatically
python -m agent.main                    # real agent (Claude); needs ANTHROPIC_API_KEY in .env
```
Bugs are written to `bugs/` as markdown, plus `bugs/triage_summary.md`.

```
agent/failures.py     reads results.xml
agent/tools.py        rerun_test, write_summary (+ re-exports the other tools)
agent/bug_tracker.py  create_bug, search_existing_bugs (markdown now; GitHub later)
agent/agent.py        tool schemas, system prompt, Claude loop, dry-run stand-in
agent/main.py         command-line entry point
```

`.env` example:
```
ANTHROPIC_API_KEY=your-key-here
```

## Triage with Claude Pro (no API key)
Open this folder in Claude Code (the Code tab in the Claude desktop app) and run:
```
/triage
```
Claude Code runs the tests, investigates each failure with the tools in `agent/cli.py`
(`list`, `details`, `rerun`, `search`, `create-bug`, `summary`), looks at the failure screenshots,
and asks you in chat before filing any bug. Instructions live in `.claude/commands/triage.md`.

```bash
venv\Scripts\python.exe -m agent.cli list     # the same tools work by hand
```

## Two ways to run the agent
| | Command | Needs |
|---|---|---|
| Claude Code | `/triage` | Claude Pro (or other Claude Code plan) |
| Python loop | `python -m agent.main` | `ANTHROPIC_API_KEY` (pay-per-use); can also run in CI |

## Next stages
- GitHub, then GitHub Actions (needs the API route for unattended runs).
