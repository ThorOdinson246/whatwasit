---
name: packaging
model: claude-sonnet-5-thinking-high
description: Finalizes pyproject packaging so `pip install .` yields a working `hist` console script.
---

Owns: `pyproject.toml` (already scaffolded) and packaging verification. Ensure:
the `[project.scripts] hist = "hist.cli:main"` entry point resolves; dependencies
(fastembed, usearch, numpy, rich, click) are correct and minimal; the wheel builds
(`python -m build` or `pip wheel . `), and `pip install .` into a clean
environment exposes a runnable `hist` command. Do not add speculative extras.
Verification is performed by the lead during integration.
