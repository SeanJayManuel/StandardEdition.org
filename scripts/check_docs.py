"""Catch obsolete documented configuration names without loading application code."""
import ast
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
known = set()
for path in (root / "boringnews").glob("*.py"):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.fullmatch(r"(?:BN_[A-Z_]+|[A-Z_]+_API_KEY)", node.value):
                known.add(node.value)
readme = (root / "README.md").read_text()
mentioned = set(re.findall(r"\bBN_[A-Z_]+\b", readme))
unknown = mentioned - known
if unknown:
    raise SystemExit("README documents unknown settings: " + ", ".join(sorted(unknown)))
print("Documented environment settings match the implementation.")
