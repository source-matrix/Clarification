from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
readme = (root / "README.md").read_text(encoding="utf-8")
links = re.findall(r"\]\(([^)]+)\)", readme)
ignored = ("http://", "https://", "mailto:", "#")
missing = []
for link in links:
    if link.startswith(ignored):
        continue
    path = link.split("#", 1)[0]
    if path and not (root / path).exists():
        missing.append(link)
if missing:
    raise SystemExit("missing local README links: " + ", ".join(missing))
print(f"checked {len(links)} README links; all local targets exist")
