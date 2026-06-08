"""Build the Revka workflow payload from a GitHub issue JSON document."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_revka_payload.py <issue.json>")

    issue = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    repository = os.environ["GITHUB_REPOSITORY"]
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo_url = f"{server_url}/{repository}"

    payload = {
        "inputs": {
            "repository": repository,
            "repository_url": repo_url,
            "clone_url": f"https://github.com/{repository}.git",
            "default_branch": os.environ.get("DEFAULT_BRANCH", "main"),
            "issue_number": issue["number"],
            "issue_title": issue["title"],
            "issue_body": issue.get("body") or "",
            "issue_url": issue["html_url"],
            "trigger_source": "github_issue",
            "demo_goal": (
                "Reproduce the reported bug, add a regression test, fix the "
                "implementation, run pytest, and open a pull request."
            ),
            "expected_commands": ["python -m pip install -e .[dev]", "python -m pytest"],
            "target_files": ["src/agentops_demo/cart.py", "tests/test_cart.py"],
        }
    }
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
