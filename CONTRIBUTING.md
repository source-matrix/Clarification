# Contributing to Clarification

Thank you for helping improve Clarification. Please open an issue before large architectural changes so the proposed behavior can be discussed.

## Local checks

Run the following before opening a pull request:

```bash
cargo fmt --all -- --check
cargo test --workspace
PYTHONPATH=bindings/python python -m unittest discover -s tests/python -v
(cd bindings/go && gofmt -l . && go test ./...)
```

Keep public APIs documented, preserve deterministic behavior, and add a regression test for every bug fix. New image operations should explain their effect on edges, alpha, color, and computational cost.

## Pull requests

A pull request should have a focused title, a short explanation of the user-facing change, tests that demonstrate the behavior, and no generated images or local binaries. Avoid committing secrets, personal data, or large media files.
