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

    payload = {
        "inputs": {
            "github_payload": json.dumps(issue, separators=(",", ":")),
            "repo_name": repository,
        }
    }
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
