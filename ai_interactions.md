# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Codex in VS Code in agent mode for every phase of PawPal+, with an `AGENTS.md` file that set the rules
for the current phase (which files it could edit, that the Scheduler must read tasks through
`Owner.get_all_tasks()`, that new dataclass fields go at the end, Python 3.9, and never editing a test just to
make it pass). The main multi-step tasks were:

- **Phase 1:** turn my class design into a Mermaid UML diagram and matching dataclass skeletons, then review them.
- **Phase 2:** implement every method in `pawpal_system.py`, write the `main.py` demo, and draft pytest tests.
- **Phase 3:** wire the Streamlit UI to my classes using `st.session_state`.
- **Phase 4:** add sorting, filtering, recurring tasks, and all-pairs conflict detection across several files.
- **Phase 5:** draft edge-case tests and debug the one that failed.
- **Phase 6:** show the new algorithms in the UI, add UI tests, and update the UML to match the final code.

**What did the agent do?**

- Created `diagrams/uml_draft.mmd` and `pawpal_system.py` skeletons, then changed `get_all_tasks()` to return
  (Pet, Task) pairs after my follow-up.
- Implemented the scheduler (priority within a time budget, fixed-time tasks first, flexible tasks in free gaps),
  the `main.py` demo, and the first tests.
- Rewrote `app.py` so every button calls my existing methods, keeping the Owner in `st.session_state`.
- Added `sort_by_time()`, `filter_tasks()`, `next_occurrence()` and `mark_task_complete()` (using `timedelta`),
  rewrote `detect_conflicts()` to check every pair, and added a midnight cutoff, changing `pawpal_system.py`,
  `main.py`, and `tests/test_pawpal.py` together.
- Wrote edge-case tests, explained why the double-complete test failed, and applied the fix I chose.
- Added a sorted and filtered task list, a **Mark complete** button, and grouped conflict warnings to the UI,
  plus 3 UI tests; wrote `diagrams/uml_final.mmd` and copied it to `diagrams/uml.mmd`.

**What did you have to verify or fix manually?**

- **Wrong example:** Codex claimed alphabetical sorting puts "low" first. I tested `sorted(['low','medium','high'])`
  and got `['high', 'low', 'medium']`, so its example was wrong even though its conclusion was right.
- **Fix that didn't fix it:** Codex suggested `ScheduledTask.pet_name` solved the lost-pet problem, but
  `get_all_tasks()` drops the pet before a ScheduledTask exists. I pushed back and had it return (Pet, Task) pairs.
- **Silent change:** Codex swapped the order of `priority` and `category` in the Task dataclass without saying so.
  My demo still worked because it used keyword arguments, but a check that passed priority positionally sorted
  everything as "medium". I found it with `dataclasses.fields(Task)` and had Codex restore the order.
- **Stacked instructions:** I appended each phase's rules to `AGENTS.md` instead of replacing them, so Codex was
  still being told "method bodies must be `pass`" in Phase 4. I rewrote the file so it has one current phase.
- **Unverified "done":** in Phase 4 Codex said it added the tests but couldn't run pytest in its own environment.
  I ran all 22 myself in my venv, then added the venv pytest command to `AGENTS.md`.
- **A bug its test plan missed:** completing the same daily task twice created two copies for tomorrow. When the
  test failed, Codex correctly said the bug was in `mark_task_complete()`, not the test, and I kept the test.
- **Display bugs in the UML:** Codex's final diagram matched my code, but rendering it showed garbled nested types
  (`list~tuple~Pet, Task~~`), `__init__` shown as a bold "init", and overlapping lines. I gave it exact
  instructions to fix all three and checked the result in mermaid.live.
- **Things it missed that I noted myself:** times stored as strings need conversion, `remove_task` assumes unique
  titles, and `Owner.preferences` isn't used by any method yet.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

**Task:** In Phase 5, plan the edge-case tests for my scheduler (sorting, recurring tasks, conflicts).

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Codex (in VS Code) | Claude (as an independent reviewer) |
| **Prompt** | "What are the most important edge cases to test for a pet scheduler with sorting and recurring tasks? Split them into happy paths and edge cases, and tell me which ones my existing tests already cover." (with `pawpal_system.py` and `tests/test_pawpal.py` attached) | Asked it to work out the edge cases worth testing for my pushed code, by actually running each case against `pawpal_system.py` before writing any tests. |
| **Response summary** | A list of happy paths and edge cases, each marked "Covered" with the matching test name, or "Not covered". | Ran 16 edge cases against my code and reported what each one returned, then drafted 12 tests from the results. |
| **What was useful** | Accurately mapped my existing tests to the plan. Suggested a case I hadn't thought of: recurrence across month, year, and leap-day boundaries. | Found a real bug before any test was written: completing the same daily task twice created two copies for tomorrow. Also confirmed behaviors that already worked (0 minutes, exact fit, back-to-back tasks, overdue tasks). |
| **Problems noticed** | Missed the double-complete case, which was the one that actually exposed a bug. Reasoned about the code instead of running it. | Missed the month/year/leap-day rollover cases. |
| **Decision** | Kept its boundary-date test. | Kept its edge cases, including the failing double-complete test. |

**Which approach did you use in your final implementation and why?**

I combined both. Codex's plan was good at seeing what was already covered and thinking about calendar edge cases,
while Claude's approach of running each case against the real code is what found the bug. My final suite has the
edge cases from both (30 logic tests, 38 in total), and I fixed `mark_task_complete()` so completing a task twice
returns `None` instead of creating a duplicate. The lesson: a test plan written by reading the code is useful, but
running the cases is what catches real bugs, and using two tools let one fill in the other's gaps.