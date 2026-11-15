# Task Result Directories Implementation Plan

> **For agentic workers:** Execute natively in the current workspace using TDD.

**Goal:** Make every benchmark write to its own `experiments/results/taskN` directory by default.

**Architecture:** Keep benchmark runners unchanged because they already honor their output directory. Fix only CLI defaults and notebook paths, then move existing result artifacts to match.

**Tech Stack:** Python 3.11, argparse, pytest, Jupyter Notebook JSON.

**Spec:** `experiments/results/README.md`

## Global Constraints

- Preserve all measured CSV/JSON data and notebook outputs.
- Do not change benchmark algorithms, metrics, seeds, or configurations.
- Keep custom `--out` overrides working.

## Tasks

- [ ] Add failing CLI behavior tests for Task 1 and Task 2 default output directories.
- [ ] Change the two CLI defaults and make the focused tests pass.
- [ ] Point Task 1 and Task 2 notebooks at their matching result directories.
- [ ] Move existing Task 1 and Task 2 artifacts without rewriting their contents.
- [ ] Update result documentation and run the full verification suite.

## Review Focus

- Default runs create task directories automatically.
- Explicit output directories still remain runner-controlled.
- Existing benchmark data is moved, not regenerated or fabricated.
- Notebook outputs remain present after the path-only edit.
- No result files remain loose in `experiments/results/` except its README.
