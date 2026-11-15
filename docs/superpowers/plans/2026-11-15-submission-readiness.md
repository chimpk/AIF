# Submission Readiness Implementation Plan

> **For agentic workers:** Execute this checklist natively in the current workspace.

**Goal:** Match the assignment PDF, remove fake submission values, and report any item that requires real team-owned data.

**Architecture:** Keep the implemented task packages unchanged unless a failing requirement test proves a code gap. Treat abstract methods and test doubles as intentional Python/test structures.

**Tech Stack:** Python 3.11, PySAT, PyGame, pytest, Ruff, mypy.

**Spec:** `2627-HK1-AI-CK (2).pdf`

## Global Constraints

- Preserve all three task implementations and experiment outputs.
- Do not invent student identities, GitHub usernames, report claims, or a demo URL.
- Required submission artifacts are source, `README.md`, `requirement.txt`, `report.pdf`, and `demo.txt`.

## Tasks

- [x] Run Ruff, mypy, pytest, CLI smoke checks, and notebook/output checks.
- [x] Map the assignment requirements to current evidence and record genuine gaps.
- [x] Remove stale scaffold wording that can be resolved from repository evidence.
- [x] Replace identity values when real values are discoverable; leave report and demo explicitly incomplete.
- [x] Re-run gates and verify no fake submission markers remain.

## Review Focus

- The large Kakuro puzzle must solve and verify successfully.
- All four Task 2 configurations must use comparable scenarios and metrics.
- Notebook outputs must remain present as required by the submission policy.
- PyGame UI and external plugin loading need smoke/integration coverage.
- Submission-only artifacts must not be claimed complete without real files or URLs.
