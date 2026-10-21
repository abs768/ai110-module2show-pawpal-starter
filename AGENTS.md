# AGENTS.md — PawPal+

## Project
Streamlit app that helps a pet owner plan daily pet care tasks. Logic lives in pawpal_system.py; UI in app.py;
CLI demo in main.py; tests in tests/.

## Current phase: Phase 6 — UI polish, documentation, reflection
- Allowed: app.py, tests/test_app.py, diagrams/uml_final.mmd, README.md, reflection.md.
- Don't change pawpal_system.py logic; the UI must call existing Scheduler methods
  (sort_by_time, filter_tasks, mark_task_complete, generate_plan, detect_conflicts, explain_plan).
- Keep every existing widget label in app.py unchanged (tests/test_app.py finds widgets by label).
- The UML must match pawpal_system.py exactly: every field, every method, correct class.

## Rules that always apply
- Classes: Owner, Pet, Task, ScheduledTask, Scheduler. Ask before adding new classes.
- UI code in app.py only calls methods from pawpal_system.py; never duplicate scheduling logic in the UI.
- The Owner lives in st.session_state["owner"] and is created only if it isn't there yet.
- No new third-party dependencies besides streamlit and pytest.
- Run tests with `.venv/bin/python -m pytest` (pytest is installed in the project venv, not system Python).
- If a test fails, explain why before changing code. Never edit a test just to make it pass.

## Style
- Python 3.9 compatible (my venv is 3.9.6): type hints, `from __future__ import annotations`.
- One-line docstrings on every method.
- Keep it simple; explain any suggestion that adds complexity before doing it.