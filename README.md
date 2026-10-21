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

## ✨ Features

- **Owner, pets, and tasks:** enter the owner's available minutes and day start, add several pets, and give each
  pet care tasks with a duration, priority, category, optional preferred time, and how often it repeats.
- **Priority-based planning:** `Scheduler.generate_plan()` takes pending tasks due today or earlier from every pet
  (via `Owner.get_all_tasks()`), ranks them with `Scheduler._sort_key()` (priority high > medium > low, then
  preferred time, then shortest first), and keeps picking tasks until the owner's minutes run out. Fixed-time tasks
  are placed at their exact time, flexible tasks fill the earliest free gaps, and tasks that would run past midnight
  are skipped.
- **Sorting by time:** `Scheduler.sort_by_time()` orders tasks chronologically and puts tasks with no preferred time
  last. It compares times as minutes, so "9:00" correctly comes before "10:00". Plans always come out in time order.
- **Filtering:** `Scheduler.filter_tasks()` filters tasks across all pets by pet name, completion status, or both.
- **Daily and weekly recurrence:** `Task.next_occurrence()` uses `timedelta` to create a copy due 1 or 7 days later.
  `Scheduler.mark_task_complete()` marks a task done and adds that copy to the pet. Future copies stay out of today's
  plan, and completing the same task twice never creates a duplicate.
- **Conflict warnings:** `Scheduler.detect_conflicts()` finds every pair of overlapping time slots and labels each one
  `[same pet]` or `[different pets]`. It returns warnings instead of crashing, and the UI groups them into one warning
  above the plan with a suggestion to move or shorten a task.
- **Plan explanations:** each planned task has a reason ("high priority; fixed at 09:00"), skipped tasks say why
  ("needs 25 min, only 10 min left"), and `Scheduler.explain_plan()` summarizes time used, skipped tasks, conflicts,
  and the sort rule.
- **Input validation:** `valid_time()` in `app.py` only accepts real 24-hour `HH:MM` times for the day start and
  preferred times. The UI also requires a task title and rejects duplicate pet names.

## 🏗️ Architecture

The final class diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (Mermaid source; paste it into
[mermaid.live](https://mermaid.live) to view). `Owner` has `Pet`s, each `Pet` has `Task`s, and the `Scheduler` reads
every pet's tasks through `Owner.get_all_tasks()` and produces `ScheduledTask`s. `app.py` (Streamlit) and `main.py`
(CLI) only call these methods, so all the logic lives in `pawpal_system.py`.

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

The suite has 38 tests:

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
- **`tests/test_app.py` (8 UI tests)** click through the Streamlit app with `AppTest`: adding pets and tasks,
  rejecting duplicates and bad times, the sorted and filtered task list, marking a task complete (which creates
  the next occurrence), and generating schedules with skip messages, conflict warnings, or a "no conflicts" message.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/bhavanishankar/ai110-module2show-pawpal-starter
collected 38 items

tests/test_app.py ........                                               [ 21%]
tests/test_pawpal.py ..............................                      [100%]

============================== 38 passed in 1.18s ==============================
```

**Confidence level: ⭐⭐⭐⭐☆ (4/5)**
All 38 tests pass, covering the happy paths and the edge cases I could think of, and writing them caught a real
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

### Main UI features (`streamlit run app.py`)

| Section | What you can do | Scheduler method used |
|---------|-----------------|-----------------------|
| 👤 Owner | Set your name, minutes available today, and day start time | stored on `Owner` |
| 🐶 Pets | Add pets (name, species, breed, age); duplicate names are rejected | `Owner.add_pet()`, `Owner.get_pet()` |
| 📝 Care tasks | Add tasks with duration, priority, category, optional time (HH:MM), and repeat (daily / weekly / once) | `Pet.add_task()` |
| Task list | See every task sorted by time; filter by pet and by pending / done | `Scheduler.sort_by_time()`, `Scheduler.filter_tasks()` |
| Mark a task done | Pick a pending task and click **Mark complete**; a message shows when the next one is due | `Scheduler.mark_task_complete()` |
| 📅 Today's schedule | Click **Generate schedule** to see the plan, conflict warnings, skipped tasks, and **Why this plan?** | `generate_plan()`, `detect_conflicts()`, `explain_plan()` |

### Example workflow

1. In **Owner**, set the name to Sam, minutes available to 40, and day start to 07:30, then click **Save owner**.
2. In **Pets**, add *Biscuit* (dog) and *Mochi* (cat). Adding *Mochi* again shows an error.
3. In **Care tasks**, add *Morning walk* for Biscuit (30 min, high, 08:00), *Give meds* for Mochi (5 min, high,
   08:10), and *Fetch* for Biscuit (20 min, low, no time). The task list shows them sorted by time:
   08:00, 08:10, then *Fetch* ("any") last. Choose **Show tasks for → Biscuit** to see only Biscuit's tasks.
4. Click **Generate schedule**. The app shows:
   - a green summary: *Planned 2 task(s) using 35 of 40 available minutes*
   - a yellow conflict warning first, because the 08:00–08:30 walk overlaps the 08:10–08:15 meds, telling you to
     move one task or shorten it
   - the plan table with a reason for each task
   - a blue note that *Fetch* was skipped: *needs 20 min, only 5 min left*
5. Under **Mark a task done**, pick *Biscuit: Morning walk* and click **Mark complete**. The app says the next one
   (daily) is due tomorrow; the task list now shows the walk as ✅ done plus a new pending walk due tomorrow,
   and it no longer appears in today's schedule.

### Key Scheduler behaviors shown

- **Priority within a time budget:** high-priority tasks are picked first; lower ones are skipped with a reason.
- **Sorting:** the task list and the plan are always in time order; untimed tasks are placed in free gaps.
- **Conflict warnings:** overlaps are shown before the plan, labelled `[same pet]` or `[different pets]`, as a
  warning rather than an error, because the owner chose those times on purpose.
- **Recurrence:** completing a daily task creates tomorrow's copy, and a weekly task creates one 7 days out.

### Sample CLI output (`python main.py`)

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

Added order:
any   | Biscuit | Fetch in the yard    | pending | due 2026-10-21
09:00 | Mochi   | Give meds            | pending | due 2026-10-21
08:00 | Biscuit | Breakfast            | pending | due 2026-10-21
any   | Mochi   | Brush coat           | pending | due 2026-10-21
07:30 | Biscuit | Morning walk         | pending | due 2026-10-21
any   | Mochi   | Puzzle feeder        | pending | due 2026-10-21

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

Biscuit tasks:
any   | Biscuit | Fetch in the yard    | pending | due 2026-10-21
08:00 | Biscuit | Breakfast            | pending | due 2026-10-21
07:30 | Biscuit | Morning walk         | done    | due 2026-10-21
07:30 | Biscuit | Morning walk         | pending | due 2026-10-22

Completed tasks:
07:30 | Biscuit | Morning walk         | done    | due 2026-10-21
any   | Mochi   | Brush coat           | done    | due 2026-10-21

Pending Mochi tasks:
09:00 | Mochi   | Give meds            | pending | due 2026-10-21
any   | Mochi   | Puzzle feeder        | pending | due 2026-10-21
any   | Mochi   | Brush coat           | pending | due 2026-10-28

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