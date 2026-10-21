# AGENTS.md — PawPal+

## Project
Streamlit app that helps a pet owner plan daily pet care tasks. Logic lives in pawpal_system.py; UI in app.py;
CLI demo in main.py; tests in tests/.

## Current phase: Phase 4 — Smarter scheduling (done; update this section for the next phase)
- Edit pawpal_system.py, main.py, tests/test_pawpal.py, README.md, reflection.md. Don't edit app.py unless I ask.
- Keep every existing method and signature working (the UI and the existing tests depend on them).
- Scheduler must read tasks via Owner.get_all_tasks() (multi-pet), never from a single pet.
- New Task fields go at the END of the dataclass so existing positional arguments don't shift.

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