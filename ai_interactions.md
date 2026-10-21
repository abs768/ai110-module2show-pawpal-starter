# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Codex in VS Code (with an AGENTS.md file limiting it to Phase 1) to turn my class design into a
Mermaid UML diagram, generate matching Python dataclass skeletons in pawpal_system.py, and then review
the skeleton for missing relationships and logic bottlenecks.

**What did the agent do?**

- Created diagrams/uml_draft.mmd with Owner, Pet, Task, Scheduler, and a ScheduledTask helper.
- Created pawpal_system.py with dataclasses, type hints, and stubbed methods (pass + docstrings).
- Ran a Python import check to confirm the file loads.
- Reviewed the skeleton and flagged: generate_plan should return ScheduledTask, string priorities
  don't sort correctly, list fields need default_factory, and get_all_tasks() loses pet ownership.
- After my follow-up, changed get_all_tasks() to return (Pet, Task) pairs and updated the UML.


**What did you have to verify or fix manually?**


- Codex claimed alphabetical sorting puts "low" first. I tested sorted(['low','medium','high']) and
  got ['high', 'low', 'medium'], so its example was wrong even though its conclusion was right.
- Codex suggested ScheduledTask.pet_name solved the lost-pet problem, but get_all_tasks() drops the pet
  before a ScheduledTask exists. I pushed back and had it return (Pet, Task) pairs instead.
- I noted issues Codex missed: times stored as strings will need conversion, remove_task assumes
  unique titles, and Owner.preferences isn't used by any method yet.




---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
