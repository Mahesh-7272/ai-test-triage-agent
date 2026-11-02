"""Run the triage agent:  python -m agent.main [--dry-run] [--yes]"""
import argparse

from agent.agent import run_claude, run_dry


def make_approver(auto_yes: bool):
    def approve(args: dict) -> bool:
        if auto_yes:
            return True
        print(f"\nAgent wants to file a bug:\n  title:    {args.get('title')}\n  severity: {args.get('severity')}")
        return input("  Approve? [y/N] ").strip().lower() == "y"
    return approve


def main():
    parser = argparse.ArgumentParser(description="AI test-failure triage agent")
    parser.add_argument("--dry-run", action="store_true", help="scripted agent, no API key needed")
    parser.add_argument("--yes", action="store_true", help="approve every bug without asking")
    args = parser.parse_args()

    approve = make_approver(args.yes)
    (run_dry if args.dry_run else run_claude)(approve)


if __name__ == "__main__":
    main()
