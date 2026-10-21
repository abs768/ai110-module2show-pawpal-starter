# AGENTS.md — PawPal+

## Project
Streamlit app that helps a pet owner plan daily pet care tasks. Logic lives in pawpal_system.py; UI in app.py.

## Current phase: Phase 1 — System design
- Only create: diagrams/uml_draft.mmd, pawpal_system.py (skeletons), and edit reflection.md section 1.
- Classes: Owner, Pet, Task, Scheduler, plus helper ScheduledTask. Do NOT add other classes.
- Use @dataclass for Task, Pet, Owner, ScheduledTask. Use field(default_factory=list) for lists.
- Method bodies must be `pass` with a one-line docstring. No scheduling logic yet.
- Do not modify app.py, README.md, or requirements.txt.

## Current phase: Phase 2 — Implementation
- Implement method logic in pawpal_system.py. Keep the existing classes and signatures from the UML.
- Allowed files: pawpal_system.py, main.py, tests/test_pawpal.py, README.md, reflection.md.
- Scheduler must read tasks via Owner.get_all_tasks() (multi-pet), never from a single pet.
- No new third-party dependencies besides pytest. Do not modify app.py yet.

## Current phase: Phase 3 — UI integration
- Edit app.py only (pawpal_system.py stays as is unless I ask).
- Store the Owner in st.session_state["owner"]; create it only if it isn't there yet.
- UI actions must call existing methods: Owner.add_pet, Owner.get_pet, Pet.add_task, Scheduler.generate_plan,
  Scheduler.detect_conflicts, Scheduler.explain_plan. Don't duplicate scheduling logic in the UI.



## Style
- Python 3.10+, type hints, `from __future__ import annotations`.
- Keep it simple; explain any suggestion that adds complexity before doing it.