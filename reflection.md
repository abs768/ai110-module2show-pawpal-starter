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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
