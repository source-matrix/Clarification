from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path

REPO = "source-matrix/Clarification"
ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "README.md",
    "CHANGELOG.md",
    "bindings/go/clarification/clarification.go",
    "bindings/lua/clarification.lua",
    "bindings/python/clarification/__init__.py",
    "bindings/python/clarification/ai.py",
    "bindings/python/pyproject.toml",
    "crates/clarification-cli/src/main.rs",
    "crates/clarification-core/src/lib.rs",
    "docs/assets/before-after/clarification-ai-final.png",
    "docs/assets/before-after/clarification-portrait-output.jpeg",
    "docs/guides/ai-backend.md",
    "docs/guides/ai-data-sources.md",
    "docs/guides/ai-evaluation-notes.md",
    "docs/guides/api.md",
    "docs/guides/claude-opus-ai-upgrade-review.md",
    "docs/guides/claude-visual-evaluation.md",
    "docs/guides/portrait-validation.md",
    "scripts/ask_claude_opus.py",
    "scripts/claude_visual_judge.py",
    "scripts/compare_ai_results.py",
    "scripts/compare_reference.py",
    "scripts/finalize_ai_output.py",
    "scripts/run_ai_face_restore.py",
]
DELETE = ["docs/assets/before-after.png"]


def gh(*args: str, payload: dict | None = None) -> dict:
    command = ["gh", "api", *args]
    environment = os.environ.copy()
    environment.update({"NO_COLOR": "1", "GH_FORCE_TTY": "0", "GH_PAGER": "cat"})
    completed = subprocess.run(
        command,
        input=None if payload is None else json.dumps(payload),
        text=True,
        check=True,
        capture_output=True,
        env=environment,
    )
    output = completed.stdout.strip()
    if not output:
        return {}
    object_start = output.find('{')
    array_start = output.find('[')
    start = object_start if object_start >= 0 else array_start
    if start < 0:
        raise ValueError(f"GitHub API returned non-JSON output: {output[:200]!r}")
    end = output.rfind('}') + 1 if object_start >= 0 else output.rfind(']') + 1
    return json.loads(output[start:end])


def main() -> None:
    ref = gh(f"repos/{REPO}/git/ref/heads/main")
    parent = ref["object"]["sha"]
    commit = gh(f"repos/{REPO}/git/commits/{parent}")
    base_tree = commit["tree"]["sha"]

    entries: list[dict[str, str | None]] = []
    for relative in FILES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        content = base64.b64encode(path.read_bytes()).decode("ascii")
        blob = gh(
            f"repos/{REPO}/git/blobs",
            "--method", "POST",
            "--input", "-",
            payload={"content": content, "encoding": "base64"},
        )
        entries.append({"path": relative, "mode": "100644", "type": "blob", "sha": blob["sha"]})

    for relative in DELETE:
        entries.append({"path": relative, "mode": "100644", "type": "blob", "sha": None})

    tree = gh(
        f"repos/{REPO}/git/trees",
        "--method", "POST",
        "--input", "-",
        payload={"base_tree": base_tree, "tree": entries},
    )
    new_commit = gh(
        f"repos/{REPO}/git/commits",
        "--method", "POST",
        "--input", "-",
        payload={
            "message": "feat: add optional AI super-resolution backend",
            "tree": tree["sha"],
            "parents": [parent],
        },
    )
    gh(
        f"repos/{REPO}/git/refs/heads/main",
        "--method", "PATCH",
        "--input", "-",
        payload={"sha": new_commit["sha"], "force": False},
    )
    print(new_commit["sha"])


if __name__ == "__main__":
    main()
