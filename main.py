from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Sam", available_minutes=90, day_start="07:30")

    biscuit = Pet("Biscuit", "dog", "Golden Retriever", 3)
    biscuit.add_task(
        Task(
            "Morning walk",
            30,
            priority="high",
            category="walk",
            preferred_time="07:30",
        )
    )
    biscuit.add_task(
        Task(
            "Breakfast",
            10,
            priority="high",
            category="feeding",
            preferred_time="08:00",
        )
    )
    biscuit.add_task(
        Task("Fetch in the yard", 20, priority="low", category="enrichment")
    )

    mochi = Pet("Mochi", "cat", "Tabby", 5)
    mochi.add_task(
        Task(
            "Give meds",
            5,
            priority="high",
            category="meds",
            preferred_time="09:00",
        )
    )
    mochi.add_task(Task("Brush coat", 15, priority="medium", category="grooming"))
    mochi.add_task(Task("Puzzle feeder", 25, priority="low", category="enrichment"))

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    columns = "{:<13} {:<10} {:<24} {:>4} {:<8}"
    divider = "-" * 63
    print("Today's Schedule for Sam (90 min available)")
    print("=" * 58)
    print(columns.format("Time", "Pet", "Task", "Min", "Priority"))
    print(divider)
    for scheduled_task in plan:
        print(
            columns.format(
                f"{scheduled_task.start_time}-{scheduled_task.end_time}",
                scheduled_task.pet_name,
                scheduled_task.task.title,
                scheduled_task.task.duration_minutes,
                scheduled_task.task.priority,
            )
        )
    print(divider)
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
