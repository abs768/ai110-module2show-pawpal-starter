from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler, title: str) -> None:
    """Generate and print an aligned schedule with its explanation."""
    plan = scheduler.generate_plan()
    columns = "{:<13} {:<10} {:<24} {:>4} {:<8}"
    divider = "-" * 63
    print()
    print(title)
    print(columns.format("Time", "Pet", "Task", "Min", "Priority"))
    print(divider)
    for slot in plan:
        print(
            columns.format(
                f"{slot.start_time}-{slot.end_time}",
                slot.pet_name,
                slot.task.title,
                slot.task.duration_minutes,
                slot.task.priority,
            )
        )
    print(divider)
    print(scheduler.explain_plan(plan))


def print_tasks(heading: str, pairs: list[tuple[Pet, Task]]) -> None:
    """Print task time, pet, title, status, and due date for each pair."""
    print()
    print(heading)
    for pet, task in pairs:
        preferred_time = task.preferred_time or "any"
        status = "done" if task.completed else "pending"
        print(
            f"{preferred_time:<5} | {pet.name:<7} | {task.title:<20} | "
            f"{status:<7} | due {task.due_date.isoformat()}"
        )


def main() -> None:
    """Demonstrate scheduling, sorting, recurrence, and task filters."""
    owner = Owner("Sam", available_minutes=90, day_start="07:30")
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    fetch = Task("Fetch in the yard", 20, priority="low")
    meds = Task("Give meds", 5, priority="high", preferred_time="09:00")
    breakfast = Task("Breakfast", 10, priority="high", preferred_time="08:00")
    brush = Task("Brush coat", 15, priority="medium", frequency="weekly")
    walk = Task("Morning walk", 30, priority="high", preferred_time="07:30")
    puzzle = Task("Puzzle feeder", 25, priority="low")

    # Add tasks in a different order from their preferred times.
    added_pairs = [
        (biscuit, fetch),
        (mochi, meds),
        (biscuit, breakfast),
        (mochi, brush),
        (biscuit, walk),
        (mochi, puzzle),
    ]
    for pet, task in added_pairs:
        pet.add_task(task)

    scheduler = Scheduler(owner)
    print_schedule(scheduler, "Today's schedule for Sam")

    print_tasks("Added order:", added_pairs)
    time_sorted = scheduler.sort_by_time([task for _, task in added_pairs])
    pet_by_task_id = {id(task): pet for pet, task in added_pairs}
    print_tasks(
        "Sorted by preferred time:",
        [(pet_by_task_id[id(task)], task) for task in time_sorted],
    )

    next_walk = scheduler.mark_task_complete(biscuit, walk)
    next_brush = scheduler.mark_task_complete(mochi, brush)
    print()
    print("Next occurrences:")
    print(f"Morning walk: {next_walk.due_date.isoformat() if next_walk else 'none'}")
    print(f"Brush coat: {next_brush.due_date.isoformat() if next_brush else 'none'}")

    print_tasks("Biscuit tasks:", scheduler.filter_tasks(pet_name="Biscuit"))
    print_tasks("Completed tasks:", scheduler.filter_tasks(completed=True))
    print_tasks(
        "Pending Mochi tasks:",
        scheduler.filter_tasks(pet_name="Mochi", completed=False),
    )

    mochi.add_task(
        Task("Vet call", 15, priority="high", preferred_time="09:00")
    )
    print_schedule(scheduler, "Schedule after adding the vet call")


if __name__ == "__main__":
    main()
