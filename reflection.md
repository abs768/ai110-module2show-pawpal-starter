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

My scheduler considers three constraints: the owner's available minutes for the day, each task's
priority (high, medium, low), and an optional preferred time (like meds at 09:00). It also only
schedules pending tasks, so anything already marked complete is left out.

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

**b. Judgment and verification**

- **Accepted:** Using owner.get_all_tasks() and the Pet from each (pet, task) pair for pet_name.
  This matched the change I made in Phase 1. I also accepted the two-step plan, because placing
  fixed-time tasks first stops a flexible task from taking a slot like meds at 09:00.
- **Added myself:** Codex didn't mention that get_all_tasks() only returns pending tasks, so
  completed tasks are filtered out without the Scheduler checking them.
- **Changed:** The first output only showed start times. I had it show start–end ranges so it's
  easy to see that no tasks overlap.
- **Fixed:** pytest only ran with a PYTHONPATH workaround because it wasn't installed in my venv.
  I installed it with `python -m pip install pytest` and added it to requirements.txt.
- **Verified:** I ran main.py and checked by hand that the plan uses 80 of 90 minutes, places
  fixed-time tasks at their times, and skips the lowest-priority task that doesn't fit. I ran
  `python -m pytest` and all 4 tests passed, including a multi-pet test and an out-of-time test.
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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
