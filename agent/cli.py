"""Command-line wrapper around the agent tools, so Claude Code can call them.

Every command prints JSON. Usage:  python -m agent.cli <command> [options]

  list                                    failed tests from reports/results.xml
  details <test_id>                       traceback, screenshot path, test source
  rerun <node_id> [--times 3]             rerun a test to check for flakiness
  search <query>                          look for already-filed bugs
  create-bug --title T --severity S --body-file F [--labels a,b]
  summary --file F                        save the triage report
Use "-" as the file name to read from stdin.
"""
import argparse
import json
import sys
from pathlib import Path

from agent import tools


def emit(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent.cli", description="Triage tools as commands")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")

    details = sub.add_parser("details")
    details.add_argument("test_id")

    rerun = sub.add_parser("rerun")
    rerun.add_argument("node_id")
    rerun.add_argument("--times", type=int, default=3)

    search = sub.add_parser("search")
    search.add_argument("query")

    bug = sub.add_parser("create-bug")
    bug.add_argument("--title", required=True)
    bug.add_argument("--severity", default="medium", choices=["low", "medium", "high", "critical"])
    bug.add_argument("--body-file", required=True)
    bug.add_argument("--labels", default="")

    summary = sub.add_parser("summary")
    summary.add_argument("--file", required=True)
    return parser


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()

    if args.command == "list":
        emit(tools.list_failures())
    elif args.command == "details":
        emit(tools.get_failure_details(args.test_id))
    elif args.command == "rerun":
        emit(tools.rerun_test(args.node_id, args.times))
    elif args.command == "search":
        emit(tools.search_existing_bugs(args.query))
    elif args.command == "create-bug":
        labels = [x.strip() for x in args.labels.split(",") if x.strip()]
        emit(tools.create_bug(args.title, read_text(args.body_file), args.severity, labels))
    elif args.command == "summary":
        emit(tools.write_summary(read_text(args.file)))


if __name__ == "__main__":
    main()
