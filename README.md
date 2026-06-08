# Google AgentOps Demo: GitHub Issue to Revka

This repository is a small, intentionally simple demo for a GitHub issue -> Revka -> pull request workflow.

The Python package has one known bug: cart subtotal calculation ignores item quantity. The baseline tests pass because they only cover quantity `1`; the demo issue asks Revka to reproduce the bug, add a regression test, fix the code, and open a PR.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

Run the demo CLI:

```bash
python -m agentops_demo
```

The sample order contains multiple quantities, so the subtotal is intentionally wrong until the issue is fixed.

## Revka Trigger Setup

Create these repository secrets:

```bash
gh secret set REVKA_GATEWAY_URL --body "https://construct.kumiho.cloud"
gh secret set REVKA_BEARER_TOKEN --body "$REVKA_BEARER_TOKEN"
```

Optionally set the workflow name if your Revka workflow is not named `github-issue-resolver`:

```bash
gh variable set REVKA_WORKFLOW_NAME --body "github-issue-resolver"
```

## Demo Flow

1. Configure the secrets above.
2. Open the demo issue in this repo.
3. Add the `revka-demo` label, or run the `Revka Issue Trigger` workflow manually with the issue number.
4. GitHub Actions sends the issue payload to Revka:

```text
POST $REVKA_GATEWAY_URL/api/workflows/run/$REVKA_WORKFLOW_NAME
Authorization: Bearer $REVKA_BEARER_TOKEN
```

The request body uses the built-in `github-issue-resolver` inputs:

```json
{
  "inputs": {
    "github_payload": "{...issue json...}",
    "repo_name": "KumihoIO/google-agentops-demo"
  }
}
```

Revka should inspect the issue, ask for human approval, reproduce the quantity bug, add a regression test, fix `subtotal_cents`, open a PR, then pause again before merge/close.
