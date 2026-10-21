# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

- Add owner and pet information, including the owner's name and available time and the pet's basic details.
- Add or edit care tasks with a duration, priority, and optional preferred time.
- Generate and view today's plan so it fits the available time, with an explanation of what was included or skipped.

**1a. Initial design**

- **Owner:** I gave Owner a name, available minutes, day start, preferences, and a list of pets. It stores owner-level planning information and provides access to the owner's pets and their tasks.
- **Pet:** I gave Pet a name, species, breed, age, and a list of tasks. It stores pet details and provides ways to manage and retrieve that pet's tasks.
- **Task:** A Task holds the details of one care activity, including its title, category, duration, priority, preferred time, frequency, and completion status. Keeping these details together makes it easier to compare tasks when building a plan.
- **Scheduler:** This is the “brain” of the app. I kept the planning responsibilities here—generating and explaining a plan, sorting tasks, checking time limits, and detecting conflicts—so Owner and Pet can stay simple data holders and scheduling can be tested on its own.
- **ScheduledTask:** I gave ScheduledTask a Task, pet name, start and end times, and a reason. It represents a task as placed in a plan.

Relationships: Owner has Pets, Pet needs Tasks, and Scheduler plans for an Owner and creates ScheduledTasks.

**1b. Design changes**

I asked the AI to review my skeleton for missing relationships and bottlenecks.

- **Changed:** The AI suggested ScheduledTask.pet_name solves lost pet ownership, but `get_all_tasks()` drops the pet before scheduling ever happens. I changed `get_all_tasks()` to return (Pet, Task) pairs so the Scheduler knows which pet each task belongs to.
- **Confirmed:** The review agreed with choices I'd already made: returning ScheduledTask from `generate_plan()` (keeps “what needs doing” separate from “when”), and using `field(default_factory=list)` so each Owner and Pet gets its own list.
- **Corrected the AI:** It said string priorities sort with “low” first. I tested `sorted(['low', 'medium', 'high'])` and got `['high', 'low', 'medium']`. The example was wrong, but the point still held, which is why I use PRIORITY_RANKS and `priority_rank()` instead of sorting strings.
- **Noted for later:** times are strings and will need conversion, `remove_task` assumes unique titles, and Owner.preferences isn't used by any method yet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three main constraints: the owner's available minutes for the day, each task's
priority (high, medium, low), and an optional preferred time (like meds at 09:00). It also only
schedules pending tasks that are due today or earlier, so completed tasks and future copies of
recurring tasks are left out. A task that would run past midnight is skipped with a reason.

I decided priority matters most because missing meds or feeding is worse than missing playtime.
Time budget comes second: the scheduler picks tasks in priority order until the minutes run out.
Preferred time comes third. It decides *where* a task goes in the day, not *whether* it gets in.
Ties are broken by earlier preferred time, then shorter duration, so more tasks can fit.

**b. Tradeoffs**

My scheduler is greedy: it takes the most important tasks first and never goes back to rearrange.
That means a long high-priority task can use up time that could have fit two shorter low-priority
tasks. In my demo, "Puzzle feeder" (25 min, low) was skipped because only 10 minutes were left.

I think that's reasonable for a busy pet owner. It's more important that the essential care always
happens than that the most total tasks fit, and a greedy approach is simple to explain. The plan
tells the owner exactly which task was skipped and why. Owner preferences are stored but not used
yet, which I'd add next.

A second tradeoff is in conflict detection. My scheduler doesn't move fixed-time tasks to avoid a clash.
If meds and a vet call are both set for 09:00, it keeps both at 09:00 and prints a warning. I chose this
because the owner picked those times for a reason, and silently moving meds could be worse than a warning.
Checking every pair of slots is O(n²) in the worst case, but with a handful of pet tasks per day that's not
a real cost, and it fixed a bug where my first version only compared neighbouring slots and missed overlaps.

---

## 3. AI Collaboration

**a. How you used AI**

I used Codex in VS Code in agent mode, with an AGENTS.md file that told it which files it could edit
and that the Scheduler must read from Owner.get_all_tasks(). Before implementing, I asked it how the
Scheduler should get tasks from the Owner's pets. Then I had it implement the methods, write main.py,
draft pytest tests, and update the README. It suggested a two-step plan: choose tasks by priority
within the time budget, then place fixed-time tasks first and fill flexible ones into free gaps.
It also suggested a table-style layout for the terminal schedule.

For the Streamlit UI, I asked Codex how to keep my Owner object from being recreated every time
Streamlit reruns the script. It explained `st.session_state` and suggested checking
`if "owner" not in st.session_state` before creating the Owner, then reusing it on later reruns.
I then had it wire the buttons to my existing methods: Add pet calls `owner.add_pet()`, Add task
calls `pet.add_task()`, and Generate schedule calls `Scheduler(owner).generate_plan()`.

For smarter scheduling, I opened a separate chat and asked Codex to brainstorm small algorithm
improvements, then had it implement them one at a time: `sort_by_time()`, `filter_tasks()`,
recurring tasks using `timedelta` (`next_occurrence()` and `mark_task_complete()`), all-pairs conflict
detection, and a midnight cutoff. Finally, I asked it how to simplify one of the algorithms.

**b. Judgment and verification**

- **Accepted:** Using owner.get_all_tasks() and the Pet from each (pet, task) pair for pet_name.
  This matched the change I made in Phase 1. I also accepted the two-step plan, because placing
  fixed-time tasks first stops a flexible task from taking a slot like meds at 09:00.
- **Added myself:** Codex didn't mention that get_all_tasks() only returns pending tasks, so
  completed tasks are filtered out without the Scheduler checking them.
- **Changed:** The first output only showed start times. I had it show start–end ranges so it's
  easy to see whether tasks overlap.
- **Fixed:** pytest only ran with a PYTHONPATH workaround because it wasn't installed in my venv.
  I installed it with `python -m pip install pytest` and added it to requirements.txt.
- **Verified:** I ran main.py and checked by hand that the plan uses 80 of 90 minutes, places
  fixed-time tasks at their times, and skips the lowest-priority task that doesn't fit.
- **Caught an AI change:** Codex silently swapped the order of `priority` and `category` in the Task
  dataclass. My demo still worked because it used keyword arguments, but a verification script that
  passed priority positionally sorted everything as "medium." I checked the field order with
  `dataclasses.fields(Task)` and had Codex restore the original order from my skeleton.
- **Accepted (UI):** The session state pattern, because it keeps one Owner for the whole session
  and the UI only calls methods from `pawpal_system.py` instead of duplicating scheduling logic.
- **Limitation:** Session state only lasts for the browser session. If I reload the page, my pets
  and tasks are gone. That's fine for this project, but saving to a JSON file would be the next step.
- **Verified (UI):** I ran `streamlit run app.py`, added two pets and some tasks, and generated a
  schedule. Adding the same pet name twice showed an error, and a bad time like "8am" was rejected.
  When I set a 40-minute budget, Fetch was skipped and the app warned that the 08:00 walk overlaps
  the 08:10 meds.
- **Phase 4 planning:** Codex suggested six improvements. I accepted all-pairs conflict detection (the
  same bug I'd found myself), filtering, and a midnight boundary check. It said plans needed sorting by
  start time, but `generate_plan()` already does that; what was missing was `sort_by_time()` for plain
  tasks. I used the assignment's "create next occurrence on completion" approach for recurring tasks
  instead of Codex's "expand into each day" idea, because it's simpler. I rejected value-based selection
  because it adds complexity and my greedy tradeoff is deliberate.
- **Evaluate & refine:** I asked Codex how to simplify `detect_conflicts()`. It said the shape was already
  efficient (sort once, compare each slot only with later slots that could overlap, and break early), but
  suggested removing a broad try/except that silently swallowed errors. I accepted that, because hiding errors
  would make bugs harder to find, and my UI already validates times. It also mentioned using index ranges
  instead of `ordered[i + 1:]` to avoid copying lists. I kept the slice, because with a handful of tasks per day
  readability matters more than that small speedup.
- **Verified (Phase 4):** Codex said it added the tests but couldn't run pytest in its own environment, so I
  ran `python -m pytest -v` in my venv myself: all 22 tests passed. I also checked that every method named in
  the README table actually exists in `pawpal_system.py` and is in the right class.

---

## 4. Testing and Verification

**a. What you tested**

I have 22 automated tests, all passing with `python -m pytest`.

Logic tests (`tests/test_pawpal.py`, 17 tests):
- `mark_complete()` changes a task's status, and `add_task()` increases a pet's task count.
- The scheduler pulls tasks from every pet through `Owner.get_all_tasks()`, not just one pet.
- When time runs out, the scheduler keeps the high-priority task and skips the low-priority one.
- `sort_by_time()` orders tasks by HH:MM and puts tasks with no time last.
- `filter_tasks()` works by pet name, by completion status, and by both together.
- Completing a daily task creates a copy due tomorrow; weekly is +7 days; "once" doesn't repeat.
- Tomorrow's copy of a completed task is left out of today's plan but appears in tomorrow's.
- Two tasks at the same time produce a warning, overlaps are found even between non-neighbouring
  slots, and conflicts are labelled same pet / different pets.
- Tasks (fixed or flexible) that would run past midnight are skipped with a reason.

UI tests (`tests/test_app.py`, 5 tests using Streamlit's AppTest to click through the app):
- Adding a pet creates a real `Pet` object that's still there after the app reruns.
- Adding the same pet name twice shows an error instead of creating a duplicate.
- A task goes to the pet I selected, not a different one.
- An invalid time like "8am" shows an error instead of crashing the app.
- Generating a schedule with a 40-minute budget shows the planned tasks, a skipped task,
  and an overlap warning.

These tests matter because they cover the core promises of the app: the right tasks get
scheduled, the most important ones win when time is short, multiple pets work together, recurring
tasks come back on the right day, and data entered in the browser actually reaches my classes and
stays there. I also checked the terminal output of `main.py` by hand.

**b. Confidence**

I'm fairly confident in the main flow: picking tasks by priority within the time budget, placing
fixed-time tasks, filling flexible ones into free gaps, sorting, filtering, and recurring tasks all
work and are tested.

Writing this section helped me find bugs. When I tried edge cases by hand, I found two real problems:
`detect_conflicts()` only compared neighbouring slots (so a 60-minute walk at 08:00 overlapping both
08:10 meds and 08:20 feeding only reported one conflict), and times weren't capped at midnight (a
60-minute task at 23:30 showed as ending at "24:30"). I fixed both in Phase 4 and added tests for them.

If I had more time, I'd test:
- an owner with no pets, or pets with no tasks (empty plan)
- an available time of 0 minutes
- two tasks with the same title (`remove_task` only removes the first one)
- a fixed-time task that is earlier than the owner's day start
- marking a task complete from the Streamlit UI

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?