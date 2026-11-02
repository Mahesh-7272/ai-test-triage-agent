"""Where bugs go. Version 1 writes markdown files into bugs/.

To use GitHub Issues later, only this file changes: keep the same two
function names and signatures.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUGS_DIR = ROOT / "bugs"

SEVERITIES = ("low", "medium", "high", "critical")


def _display_path(path: Path) -> str:
    """Show paths relative to the project when possible."""
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def _next_number(bugs_dir: Path) -> int:
    numbers = [int(m.group(1)) for p in bugs_dir.glob("BUG-*.md")
               if (m := re.match(r"BUG-(\d+)", p.name))]
    return max(numbers, default=0) + 1


def search_existing_bugs(query: str, bugs_dir: Path = BUGS_DIR) -> list[dict]:
    """Find bugs whose title or body contains any word (3+ letters) of the query."""
    if not bugs_dir.exists():
        return []
    words = [w for w in re.findall(r"[a-z0-9_]+", query.lower()) if len(w) >= 3]
    found = []
    for path in sorted(bugs_dir.glob("BUG-*.md")):
        text = path.read_text(encoding="utf-8")
        hits = sum(1 for w in words if w in text.lower())
        if hits:
            title = text.splitlines()[0].lstrip("# ").strip()
            found.append({"bug_id": path.stem.split("-")[0] + "-" + path.stem.split("-")[1],
                          "title": title, "file": _display_path(path), "matching_words": hits})
    return sorted(found, key=lambda b: -b["matching_words"])


def create_bug(title: str, body: str, severity: str = "medium",
               labels: list[str] | None = None, bugs_dir: Path = BUGS_DIR) -> dict:
    """Write one bug as BUG-001-some-title.md and return its id and path."""
    if severity not in SEVERITIES:
        return {"error": f"severity must be one of {SEVERITIES}"}
    bugs_dir.mkdir(parents=True, exist_ok=True)
    number = _next_number(bugs_dir)
    bug_id = f"BUG-{number:03d}"
    path = bugs_dir / f"{bug_id}-{_slug(title)}.md"
    content = (
        f"# {bug_id}: {title}\n\n"
        f"**Severity:** {severity}  \n"
        f"**Labels:** {', '.join(labels or [])}\n\n"
        f"{body.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return {"bug_id": bug_id, "file": _display_path(path)}
