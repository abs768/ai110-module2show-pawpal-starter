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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Sam (90 min available)
==========================================================
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
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.10.20, pytest-8.3.2, pluggy-1.6.0
rootdir: /Users/bhavanishankar/ai110-module2show-pawpal-starter
collected 4 items

tests/test_pawpal.py ....                                                [100%]

============================== 4 passed in 0.00s ===============================
```

## Implementation Summary

Task holds one care activity and its details, while each Pet holds that pet's tasks. Owner holds its pets and exposes `get_all_tasks()` as (pet, task) pairs, so Scheduler knows which pet each task belongs to. Scheduler reads tasks through `get_all_tasks()` and picks tasks by priority within the owner's time budget. It places tasks with fixed preferred times first, then fills flexible tasks into the earliest free gaps. It also explains why tasks were skipped and reports conflicts in the plan.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
