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
python -m pytest        # tests
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
python -m pytest
```

The suite has 35 tests:

- **`tests/test_pawpal.py` (30 logic tests)**
  - *Core:* task completion, adding tasks, multi-pet scheduling, time budget (including exact fit and 0 minutes)
  - *Sorting:* `sort_by_time()` is chronological (untimed last, "9:00" before "10:00"); generated plans come out in time order
  - *Filtering:* by pet, by completion status, and both
  - *Recurring:* daily → next day, weekly → +7 days, "once" doesn't repeat, month/year/leap-day rollover,
    future copies stay out of today's plan, overdue tasks are still planned, and completing a task twice
    doesn't create duplicates
  - *Conflicts:* duplicate times for the same pet and for different pets are flagged, three tasks at one time give
    three warnings, non-neighbouring overlaps are found, back-to-back tasks are *not* conflicts
  - *Edge cases:* owner with no pets, pet with no tasks, tasks running past midnight, flexible tasks filling gaps
- **`tests/test_app.py` (5 UI tests)** click through the Streamlit app with `AppTest`: adding pets and tasks,
  rejecting duplicates and bad times, and generating a schedule with skip and conflict messages.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/bhavanishankar/ai110-module2show-pawpal-starter
collected 35 items

tests/test_app.py .....                                                  [ 14%]
tests/test_pawpal.py ..............................                      [100%]

============================== 35 passed in 1.01s ==============================
```

**Confidence level: ⭐⭐⭐⭐☆ (4/5)**
All 35 tests pass, covering the happy paths and the edge cases I could think of, and writing them caught a real
bug (completing a task twice created a duplicate next occurrence), which I fixed. I'm not giving 5 stars because
some behavior is untested or intentionally simple: fixed-time tasks before the owner's day start are allowed,
`remove_task` only removes the first task with a given title, owner preferences aren't used yet, and data isn't
saved between browser sessions.

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
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily task adds a copy due tomorrow, a weekly one in 7 days (`timedelta`); future copies stay out of today's plan; completing a task twice doesn't create a duplicate |

## 📸 Demo Walkthrough

1. Run `streamlit run app.py` and set the owner's name, minutes available today, and day start time, then click **Save owner**.
2. Add pets (for example Biscuit the dog and Mochi the cat). Duplicate names are rejected.
3. Add care tasks for each pet with a duration, priority, category, and optional preferred time (HH:MM).
4. Click **Generate schedule** to see a time-ordered plan with the reason for each task.
5. Read the messages below the plan: skipped tasks explain why they didn't fit, conflict warnings show overlapping
   times, and **Why this plan?** explains the sorting rule.