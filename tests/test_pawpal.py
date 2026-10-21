from datetime import date, timedelta

from pawpal_system import Owner, Pet, ScheduledTask, Scheduler, Task


def test_mark_complete_changes_status() -> None:
    task = Task("Feed", 10, completed=False)

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet("Biscuit", "dog")
    task = Task("Walk", 30)

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1


def test_scheduler_uses_tasks_from_all_pets() -> None:
    owner = Owner("Sam")
    dog = Pet("Biscuit", "dog")
    cat = Pet("Mochi", "cat")
    dog.add_task(Task("Walk", 30))
    cat.add_task(Task("Play", 15))
    owner.add_pet(dog)
    owner.add_pet(cat)

    plan = Scheduler(owner).generate_plan()

    assert {scheduled_task.pet_name for scheduled_task in plan} == {
        "Biscuit",
        "Mochi",
    }


def test_scheduler_skips_low_priority_when_out_of_time() -> None:
    owner = Owner("Sam", available_minutes=30)
    pet = Pet("Biscuit", "dog")
    pet.add_task(Task("Walk", 30, priority="high"))
    pet.add_task(Task("Fetch", 20, priority="low"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()

    assert [scheduled_task.task.title for scheduled_task in plan] == ["Walk"]
    assert scheduler.skipped[0][1].title == "Fetch"


def test_sort_by_time_places_untimed_tasks_last() -> None:
    """Sort preferred times chronologically and put untimed tasks last."""
    scheduler = Scheduler(Owner("Sam"), day=date(2026, 10, 21))
    tasks = [
        Task("Any", 5),
        Task("Late", 5, preferred_time="18:00"),
        Task("Early", 5, preferred_time="07:05"),
    ]

    assert [task.title for task in scheduler.sort_by_time(tasks)] == [
        "Early",
        "Late",
        "Any",
    ]


def test_filter_tasks_by_pet_name() -> None:
    """Filter task pairs by pet name."""
    dog = Pet("Biscuit", "dog", tasks=[Task("Walk", 10)])
    cat = Pet("Mochi", "cat", tasks=[Task("Feed", 5)])
    owner = Owner("Sam", pets=[dog, cat])

    assert [(pet.name, task.title) for pet, task in Scheduler(owner).filter_tasks(pet_name="Biscuit")] == [
        ("Biscuit", "Walk")
    ]


def test_filter_tasks_by_completed_status() -> None:
    """Filter task pairs by completion status."""
    pet = Pet("Biscuit", "dog", tasks=[Task("Walk", 10, completed=True), Task("Feed", 5)])
    scheduler = Scheduler(Owner("Sam", pets=[pet]))

    assert [task.title for _, task in scheduler.filter_tasks(completed=True)] == ["Walk"]


def test_filter_tasks_by_pet_name_and_completed_status() -> None:
    """Filter task pairs by both pet name and completion status."""
    dog = Pet("Biscuit", "dog", tasks=[Task("Walk", 10, completed=True), Task("Feed", 5)])
    cat = Pet("Mochi", "cat", tasks=[Task("Meds", 5, completed=True)])
    scheduler = Scheduler(Owner("Sam", pets=[dog, cat]))

    pairs = scheduler.filter_tasks(pet_name="Biscuit", completed=True)

    assert [(pet.name, task.title) for pet, task in pairs] == [("Biscuit", "Walk")]


def test_completing_daily_task_adds_next_occurrence() -> None:
    """Complete a daily task and add its pending next occurrence."""
    today = date(2026, 10, 21)
    task = Task("Walk", 30, due_date=today)
    pet = Pet("Biscuit", "dog", tasks=[task])

    next_task = Scheduler(Owner("Sam", pets=[pet]), day=today).mark_task_complete(pet, task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_weekly_next_occurrence_is_seven_days_later() -> None:
    """Advance weekly task occurrences by seven days."""
    today = date(2026, 10, 21)
    task = Task("Brush", 15, frequency="weekly", due_date=today)

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=7)


def test_once_task_has_no_next_occurrence() -> None:
    """Return no next occurrence for a non-recurring task."""
    assert Task("Vet", 15, frequency="once", due_date=date(2026, 10, 21)).next_occurrence() is None


def test_completed_daily_task_is_only_planned_on_tomorrow() -> None:
    """Plan the new daily occurrence on its due date, not today."""
    today = date(2026, 10, 21)
    pet = Pet("Biscuit", "dog")
    task = Task("Walk", 30, due_date=today)
    pet.add_task(task)
    scheduler = Scheduler(Owner("Sam", pets=[pet]), day=today)
    scheduler.mark_task_complete(pet, task)

    assert scheduler.generate_plan() == []
    assert len(Scheduler(scheduler.owner, day=today + timedelta(days=1)).generate_plan()) == 1


def test_same_pet_overlapping_tasks_report_one_conflict() -> None:
    """Report one same-pet conflict with both task titles."""
    pet = Pet("Biscuit", "dog")
    walk = Task("Walk", 30)
    meds = Task("Meds", 10)
    plan = [
        ScheduledTask(walk, pet.name, "09:00", "09:30"),
        ScheduledTask(meds, pet.name, "09:00", "09:10"),
    ]

    conflicts = Scheduler(Owner("Sam", pets=[pet])).detect_conflicts(plan)

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0] and "Meds" in conflicts[0]
    assert "overlaps" in conflicts[0] and "[same pet]" in conflicts[0]


def test_conflict_detection_finds_all_overlaps() -> None:
    """Find both overlaps involving a long task and later tasks."""
    plan = [
        ScheduledTask(Task("Walk", 60), "Biscuit", "08:00", "09:00"),
        ScheduledTask(Task("Meds", 5), "Mochi", "08:10", "08:15"),
        ScheduledTask(Task("Feed", 10), "Mochi", "08:20", "08:30"),
    ]

    conflicts = Scheduler(Owner("Sam")).detect_conflicts(plan)

    assert len(conflicts) == 2
    assert any("Walk" in conflict and "Meds" in conflict for conflict in conflicts)
    assert any("Walk" in conflict and "Feed" in conflict for conflict in conflicts)


def test_task_that_runs_past_midnight_is_skipped() -> None:
    """Skip flexible tasks that would end after midnight."""
    today = date(2026, 10, 21)
    pet = Pet("Biscuit", "dog", tasks=[Task("Long walk", 60, due_date=today)])
    scheduler = Scheduler(
        Owner("Sam", available_minutes=60, day_start="23:30", pets=[pet]),
        day=today,
    )

    assert scheduler.generate_plan() == []
    assert "midnight" in scheduler.skipped[0][2]


def test_fixed_task_that_runs_past_midnight_is_skipped() -> None:
    """Skip fixed-time tasks that would end after midnight."""
    today = date(2026, 10, 21)
    pet = Pet(
        "Biscuit",
        "dog",
        tasks=[Task("Late walk", 60, preferred_time="23:30", due_date=today)],
    )
    scheduler = Scheduler(Owner("Sam", available_minutes=60, pets=[pet]), day=today)

    assert scheduler.generate_plan() == []
    assert "midnight" in scheduler.skipped[0][2]


def test_conflict_between_different_pets_is_labeled() -> None:
    """Label overlapping tasks for different pets in the conflict warning."""
    plan = [
        ScheduledTask(Task("Walk", 30), "Biscuit", "09:00", "09:30"),
        ScheduledTask(Task("Meds", 10), "Mochi", "09:00", "09:10"),
    ]

    conflicts = Scheduler(Owner("Sam")).detect_conflicts(plan)

    assert len(conflicts) == 1
    assert "[different pets]" in conflicts[0]
