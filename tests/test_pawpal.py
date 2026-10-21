from pawpal_system import Owner, Pet, Scheduler, Task


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
