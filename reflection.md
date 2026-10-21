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

Comparing `diagrams/uml_draft.mmd` with `diagrams/uml_final.mmd` shows how the design grew during the build. The
same five classes survived from Phase 1, but I added recurrence (`due_date`, `next_occurrence()`), filtering
(`filter_tasks()`, `get_all_tasks(include_completed)`), a planning `day` on the Scheduler, and a new
Scheduler → Pet interaction for adding the next copy of a recurring task.

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

For testing, I started another new chat and asked Codex for a test plan: "What are the most important
edge cases to test for a pet scheduler with sorting and recurring tasks?" It mapped which cases my
existing tests already covered and listed the gaps. I then had it draft edge-case tests, and when one
failed, I asked it whether the bug was in my test code or my `pawpal_system.py` logic.

For the final polish, I used one more new chat. I asked Codex how conflict warnings should be presented in the UI
and which Scheduler methods `app.py` wasn't using yet, then had it update the UI to show sorting, filtering, and
recurring tasks. I attached `pawpal_system.py` and asked what my Phase 1 UML was missing, saved the final diagram as
`diagrams/uml_final.mmd`, and had it draft a Features list for the README, which I checked against the code.

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
- **Test plan (Phase 5):** Codex correctly mapped my existing tests to its plan and suggested one case I
  hadn't thought of: recurrence across month, year, and leap-day boundaries. I added it. But its plan missed
  the case that actually exposed a bug (completing the same task twice), so I added that myself, along with
  0 minutes available, an exact-fit task, overdue tasks, and three tasks at the same time.
- **Debugging (Phase 5):** When the double-complete test failed, I asked Codex whether the bug was in the
  test or my code. It said the logic was the problem: `mark_task_complete()` never checked whether the task
  was already done. It also pointed out that the test encodes a design rule I chose. I agreed with that
  rule, because a double-click in the app shouldn't create duplicate walks, so I fixed the code instead of
  changing the test.
- **Skipped (Phase 5):** Codex suggested testing invalid time strings like "8am" in the scheduler. That's true
  (`to_minutes` would raise), but my UI already rejects bad times before they reach the scheduler, and
  `test_bad_time_is_rejected_without_crashing` covers that, so I left it as a next step.

- **UI review (Phase 6):** Codex correctly found that `app.py` wasn't using `sort_by_time()`, `filter_tasks()`, or
  `mark_task_complete()`. It recommended showing each conflict with both tasks, pets, and time ranges, plus a
  suggestion to move one task. I agreed, but **modified** one part: instead of one warning per conflict, I grouped all
  conflicts into one warning shown *above* the plan, so three tasks at 09:00 don't flood the page with three boxes
  and the owner sees what to fix before reading the schedule.
- **Kept the UI thin (Phase 6):** I told Codex to keep every widget label unchanged, because my UI tests find widgets
  by label, and to only call existing Scheduler methods, so the UI has no scheduling logic of its own. One
  Streamlit detail: the "Marked done" message would vanish because `st.rerun()` clears the page, so it's kept in
  `st.session_state` and shown on the next run.
- **UML review (Phase 6):** Codex's list of UML updates was accurate, and it caught something I'd missed: a
  `Scheduler ..> Pet` relationship, because `mark_task_complete()` adds the next copy *to the pet*. Before using its
  `Pet | None` return-type style, I rendered a test diagram to make sure Mermaid shows `|` correctly. I kept the
  private helpers but shortened their parameter lists, because a long signature overlapped other text when rendered.
  When Codex wrote `uml_final.mmd`, the content matched my code, but rendering it showed three display bugs:
  nested types like `list~tuple~Pet, Task~~` came out garbled, `__init__` rendered as a bold "init" (Mermaid reads
  `__` as markdown), and `_make_slot` overlapped the line above. I switched to `list~tuple~` with `%%` comments
  explaining the pairs, moved the constructor note into a comment, and shortened the helper signatures. The
  lesson: a diagram that's *correct* still has to be *checked visually*.
- **Features list (Phase 6):** Codex's draft named the right method for each feature and added `valid_time()` for
  input validation, which I'd described too vaguely. It left out that fixed-time tasks keep their exact time and
  that completing a task twice doesn't duplicate it, so I added those back.
- **Verified (Phase 6):** `python -m pytest` gave 38 passed (8 UI + 30 logic). I also ran through the README's
  example workflow in the app to confirm the numbers it describes (35 of 40 minutes, Fetch skipped with 5 minutes
  left, one conflict warning).

---

## 4. Testing and Verification

**a. What you tested**

I have 38 automated tests, all passing with `python -m pytest`.

Logic tests (`tests/test_pawpal.py`, 30 tests):
- **Core:** `mark_complete()` changes a task's status, `add_task()` increases a pet's task count, and the
  scheduler pulls tasks from every pet through `Owner.get_all_tasks()`, not just one pet.
- **Time budget:** when time runs out, the high-priority task wins and the low-priority one is skipped with a
  reason; a task that exactly fills the budget still fits; with 0 minutes, everything is skipped.
- **Sorting:** `sort_by_time()` is chronological, puts untimed tasks last, and handles "9:00" before "10:00";
  generated plans come out in time order even when priority order is different.
- **Filtering:** `filter_tasks()` works by pet name, by completion status, and by both together.
- **Recurring tasks:** daily → tomorrow, weekly → +7 days, "once" doesn't repeat; dates roll over month, year,
  and leap-day boundaries correctly; tomorrow's copy stays out of today's plan; overdue tasks are still
  planned; completing the same task twice doesn't create a duplicate.
- **Conflicts:** duplicate times are flagged for the same pet and for different pets; three tasks at the
  same time give three warnings; overlaps between non-neighbouring slots are found; back-to-back tasks
  (one ends at 08:30, the next starts at 08:30) are *not* conflicts.
- **Edge cases:** an owner with no pets and a pet with no tasks both give an empty plan without errors;
  tasks that would run past midnight are skipped; flexible tasks fill the gap before a fixed task.

UI tests (`tests/test_app.py`, 8 tests using Streamlit's AppTest to click through the app):
- Adding a pet creates a real `Pet` object that's still there after the app reruns.
- Adding the same pet name twice shows an error instead of creating a duplicate.
- A task goes to the pet I selected, not a different one.
- An invalid time like "8am" shows an error instead of crashing the app.
- Generating a schedule with a 40-minute budget shows the planned tasks, a skipped task,
  and an overlap warning.
- The task list is sorted by time and can be filtered by pet (added in Phase 6).
- Clicking **Mark complete** on a daily task creates tomorrow's copy and shows when it's due (Phase 6).
- A schedule with no overlaps shows a "No time conflicts" message instead of a warning (Phase 6).

These tests matter because they cover the core promises of the app: the right tasks get
scheduled, the most important ones win when time is short, multiple pets work together, recurring
tasks come back on the right day exactly once, and data entered in the browser actually reaches my
classes and stays there. I also checked the terminal output of `main.py` by hand.

**b. Confidence**

**Confidence: 4/5.** I'm confident in the main flow: picking tasks by priority within the time budget,
placing fixed-time tasks, filling flexible ones into free gaps, sorting, filtering, recurring tasks, and
conflict detection all work and are tested, including the edge cases.

Testing found real bugs at every stage. While writing my first confidence section, I tried edge cases
by hand and found that `detect_conflicts()` only compared neighbouring slots and that times weren't capped
at midnight; I fixed both in Phase 4. In Phase 5, a new edge-case test failed: marking the same daily task
complete twice created a second copy for tomorrow. The bug was in `mark_task_complete()`, which didn't check
whether the task was already done. I added that check and all 35 tests passed.

I'm not at 5/5 because a few behaviors are untested or intentionally simple. If I had more time, I'd test:
- a fixed-time task earlier than the owner's day start (currently allowed: meds at 07:00 still go at 07:00)
- two tasks with the same title (`remove_task` only removes the first one)
- invalid time strings passed straight to the scheduler (the UI blocks them, but `to_minutes` would raise)
- editing or deleting a task from the Streamlit UI (not built yet)

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how cleanly the logic and the UI are separated. All the scheduling rules live in
`pawpal_system.py`, and both `main.py` and the Streamlit app only call those methods. That paid off over and over:
when I added sorting, filtering, and recurring tasks in Phase 4, the UI needed no logic of its own in Phase 6, just
calls to `sort_by_time()`, `filter_tasks()`, and `mark_task_complete()`. I'm also proud of the test suite. It
grew from 4 tests to 38, it covers both the logic and the UI, and it caught real bugs along the way (missed
overlaps, times past midnight, and duplicate copies when completing a task twice).

**b. What you would improve**

- **Save data between sessions.** Everything lives in `st.session_state`, so a page reload wipes it. I'd save the
  Owner to a JSON file.
- **Use owner preferences.** `Owner.preferences` has been in the design since Phase 1, but no method uses it. I'd
  let it influence placement, for example "walks in the morning".
- **Smarter conflict handling.** Right now conflicts are only warnings. I'd offer to move a flexible task, and
  warn when a fixed-time task is earlier than the owner's day start.
- **Editing and removing tasks in the UI.** The README scenario mentions add/edit; the app only adds and
  completes tasks.
- **Unique task IDs.** Titles aren't unique, so `remove_task(title)` only removes the first match.

**c. Key takeaway**

The most important thing I learned is that with a powerful AI tool, my job shifts from writing every line to being
the **lead architect**: I decide what the system is, and the AI helps build it inside those boundaries. The AI was
fast and usually right, but "usually" isn't enough. It silently reordered dataclass fields, gave a wrong example
of how strings sort, suggested a fix (`ScheduledTask.pet_name`) that didn't solve the real problem, reported tests
as done without running them, and wrote a test plan that missed the one case that exposed a bug. Every one of those
was caught because I had a clear design to compare against and I verified results myself: running the code,
running the tests, and checking the README against the actual code. Good design plus independent verification is
what made AI help safe to use.

**AI strategy**

- **Most effective features:** agent mode for multi-file changes (it updated `pawpal_system.py`, `main.py`, and the
  tests together and ran them); the chat for "explain only, don't edit yet" questions, like how `st.session_state`
  works or which strategy to use for conflict detection; and an `AGENTS.md` file with standing rules (only call
  existing methods from the UI, keep new dataclass fields at the end, never edit a test just to make it pass,
  Python 3.9). The rules file did the most to keep Codex consistent from phase to phase.
- **A suggestion I modified or rejected:** In Phase 4, Codex suggested value-based task selection, which is
  essentially a knapsack algorithm, to fit more tasks into the time budget. I rejected it: it's harder to explain
  to a pet owner, and my design deliberately uses a greedy priority rule so essential care always comes first.
  I also changed its recurring-task idea from "expand tasks into each planning day" to the simpler "create the
  next occurrence when a task is completed". Both choices kept the design small and easy to explain.
- **Separate chat sessions:** I used a new chat for each phase (design, implementation, UI, algorithms, testing,
  polish). Each chat only held the context for that phase, so Codex didn't mix old instructions into new work,
  for example it didn't keep writing stubs after the skeleton phase. It also made it easy to compare its test
  plan with my existing tests without the implementation discussion in the way, and it gave me a clean record of
  what I asked for in each phase. When I forgot to update `AGENTS.md` between phases, the old phase rules piled up
  and contradicted each other, which showed me how much the AI depends on the context I give it.