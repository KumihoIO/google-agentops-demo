"""Register or update a workflow definition in a Revka gateway."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def request_json(
    method: str,
    url: str,
    token: str,
    body: dict[str, object] | None = None,
) -> tuple[int, str]:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def workflow_path_from_kref(kref: str) -> str:
    if kref.startswith("kref://"):
        return kref.removeprefix("kref://")
    return kref


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: register_revka_workflow.py <workflow.yaml>")

    gateway = os.environ["REVKA_GATEWAY_URL"].rstrip("/")
    token = os.environ["REVKA_BEARER_TOKEN"].strip()
    workflow_path = Path(sys.argv[1])
    definition = workflow_path.read_text(encoding="utf-8")

    name = workflow_path.stem
    body = {
        "name": name,
        "description": "GitHub issue to Revka demo resolver",
        "definition": definition,
        "tags": ["github", "issue", "demo", "python", "revka"],
    }

    list_status, list_text = request_json(
        "GET",
        f"{gateway}/api/workflows?include_deprecated=true&include_definition=false",
        token,
    )
    if not 200 <= list_status < 300:
        print(f"Failed to list workflows: HTTP {list_status}")
        print(list_text)
        raise SystemExit(1)

    parsed = json.loads(list_text or "[]")
    workflows = parsed.get("workflows", parsed) if isinstance(parsed, dict) else parsed
    existing = next(
        (
            wf
            for wf in workflows
            if wf.get("name") == name or wf.get("item_name") == name
        ),
        None,
    )

    if existing:
        kref_path = workflow_path_from_kref(existing["kref"])
        status, text = request_json(
            "PUT",
            f"{gateway}/api/workflows/{kref_path}",
            token,
            body,
        )
        action = "updated"
    else:
        status, text = request_json("POST", f"{gateway}/api/workflows", token, body)
        action = "created"

    print(f"Revka workflow {action}: HTTP {status}")
    print(text)
    if not 200 <= status < 300:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

