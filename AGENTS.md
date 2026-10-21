# AGENTS.md — PawPal+

## Project
Streamlit app that helps a pet owner plan daily pet care tasks. Logic lives in pawpal_system.py; UI in app.py;
CLI demo in main.py; tests in tests/.

## Current phase: Phase 5 — Testing and verification
- Main file: tests/test_pawpal.py. Also allowed: README.md, reflection.md.
- Only change pawpal_system.py to fix a bug a test exposes, and explain the bug first.
- Tests use a fixed date (date(2026, 10, 21)) instead of date.today() so they don't depend on the clock.
- Use keyword arguments for Task fields after duration (priority=, preferred_time=, due_date=).
- Keep every existing method and signature working (the UI and the existing tests depend on them).
- Scheduler must read tasks via Owner.get_all_tasks() (multi-pet), never from a single pet.

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