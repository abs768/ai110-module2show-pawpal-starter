# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run it

```bash
python main.py          # CLI demo
streamlit run app.py    # web app
python -m pytest -v     # tests
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output of `python main.py` (two pets, tasks added out of order, recurring tasks, and a conflict):

```
Today's schedule for Sam
Time          Pet        Task                      Min Priority
---------------------------------------------------------------
07:30-08:00   Biscuit    Morning walk               30 high
08:00-08:10   Biscuit    Breakfast                  10 high
08:10-08:25   Mochi      Brush coat                 15 medium
08:25-08:45   Biscuit    Fetch in the yard          20 low
09:00-09:05   Mochi      Give meds                   5 high
---------------------------------------------------------------
Scheduled 5 task(s) using 80 of 90 available minutes.
Sort rule: (high > medium > low), then preferred time, then shortest first
Skipped 'Puzzle feeder' for Mochi: needs 25 min, only 10 min left.

Sorted by preferred time:
07:30 | Biscuit | Morning walk         | pending | due 2026-10-21
08:00 | Biscuit | Breakfast            | pending | due 2026-10-21
09:00 | Mochi   | Give meds            | pending | due 2026-10-21
any   | Biscuit | Fetch in the yard    | pending | due 2026-10-21
any   | Mochi   | Brush coat           | pending | due 2026-10-21
any   | Mochi   | Puzzle feeder        | pending | due 2026-10-21

Next occurrences:
Morning walk: 2026-10-22
Brush coat: 2026-10-28

Completed tasks:
07:30 | Biscuit | Morning walk         | done    | due 2026-10-21
any   | Mochi   | Brush coat           | done    | due 2026-10-21

Schedule after adding the vet call
Time          Pet        Task                      Min Priority
---------------------------------------------------------------
07:30-07:50   Biscuit    Fetch in the yard          20 low
08:00-08:10   Biscuit    Breakfast                  10 high
08:10-08:35   Mochi      Puzzle feeder              25 low
09:00-09:05   Mochi      Give meds                   5 high
09:00-09:15   Mochi      Vet call                   15 high
---------------------------------------------------------------
Scheduled 5 task(s) using 75 of 90 available minutes.
Sort rule: (high > medium > low), then preferred time, then shortest first
Conflict: 'Give meds' for Mochi (09:00-09:05) overlaps 'Vet call' for Mochi (09:00-09:15) [same pet]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite (from the repo root, with .venv active):
python -m pytest -v
```

The suite has 22 tests: 17 logic tests in `tests/test_pawpal.py` (task completion, multi-pet scheduling,
time budget, sorting, filtering, recurring tasks, conflicts, midnight cutoff) and 5 UI tests in
`tests/test_app.py` that click through the Streamlit app with `AppTest`.

Sample test output:

```
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 22 items

tests/test_app.py::test_add_pet_creates_pet_object_that_persists PASSED
tests/test_app.py::test_duplicate_pet_name_is_rejected PASSED
tests/test_app.py::test_add_task_goes_to_selected_pet PASSED
tests/test_app.py::test_bad_time_is_rejected_without_crashing PASSED
tests/test_app.py::test_generate_schedule_skips_and_warns PASSED
tests/test_pawpal.py::test_mark_complete_changes_status PASSED
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED
tests/test_pawpal.py::test_scheduler_uses_tasks_from_all_pets PASSED
tests/test_pawpal.py::test_scheduler_skips_low_priority_when_out_of_time PASSED
tests/test_pawpal.py::test_sort_by_time_places_untimed_tasks_last PASSED
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED
tests/test_pawpal.py::test_filter_tasks_by_completed_status PASSED
tests/test_pawpal.py::test_filter_tasks_by_pet_name_and_completed_status PASSED
tests/test_pawpal.py::test_completing_daily_task_adds_next_occurrence PASSED
tests/test_pawpal.py::test_weekly_next_occurrence_is_seven_days_later PASSED
tests/test_pawpal.py::test_once_task_has_no_next_occurrence PASSED
tests/test_pawpal.py::test_completed_daily_task_is_only_planned_on_tomorrow PASSED
tests/test_pawpal.py::test_same_pet_overlapping_tasks_report_one_conflict PASSED
tests/test_pawpal.py::test_conflict_detection_finds_all_overlaps PASSED
tests/test_pawpal.py::test_task_that_runs_past_midnight_is_skipped PASSED
tests/test_pawpal.py::test_fixed_task_that_runs_past_midnight_is_skipped PASSED
tests/test_pawpal.py::test_conflict_between_different_pets_is_labeled PASSED

============================== 22 passed in 0.90s ==============================
```

## Implementation Summary

Task holds one care activity and its details, while each Pet holds that pet's tasks. Owner holds its pets and
exposes `get_all_tasks()` as (pet, task) pairs, so Scheduler knows which pet each task belongs to. Scheduler
reads tasks through `get_all_tasks()` and picks tasks by priority within the owner's time budget. It places tasks
with fixed preferred times first, then fills flexible tasks into the earliest free gaps. It also explains why
tasks were skipped and reports conflicts in the plan. Scheduler can also sort tasks by time, filter them by pet
or completion status, and create the next occurrence of a daily or weekly task when it's marked complete.

The Streamlit app (`app.py`) keeps the Owner in `st.session_state`, so pets and tasks persist between clicks,
and every button calls these same methods instead of duplicating the logic.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time` orders tasks by HH:MM (untimed tasks last); the planner ranks by priority, then preferred time, then shortest |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)`, `Owner.get_all_tasks(include_completed)` | Filter by pet, by done/pending, or both; tasks that don't fit the time budget or would run past midnight are skipped with a reason |
| Conflict handling | `Scheduler.detect_conflicts()` | Sorts slots once, then compares each with every later slot that could overlap; labels `[same pet]` / `[different pets]` and returns warnings instead of crashing |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily task adds a copy due tomorrow, a weekly one in 7 days (`timedelta`); future copies stay out of today's plan |

## 📸 Demo Walkthrough

1. Run `streamlit run app.py` and set the owner's name, minutes available today, and day start time, then click **Save owner**.
2. Add pets (for example Biscuit the dog and Mochi the cat). Duplicate names are rejected.
3. Add care tasks for each pet with a duration, priority, category, and optional preferred time (HH:MM).
4. Click **Generate schedule** to see a time-ordered plan with the reason for each task.
5. Read the messages below the plan: skipped tasks explain why they didn't fit, conflict warnings show overlapping
   times, and **Why this plan?** explains the sorting rule.