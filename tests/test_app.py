from pathlib import Path
from datetime import timedelta

from streamlit.testing.v1 import AppTest


APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 30


def start_app():
    """Start the PawPal Streamlit app and check for startup errors."""
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    assert not at.exception
    return at


def widget(at, kind, label):
    """Find the first widget of a kind with the given label."""
    return next(item for item in getattr(at, kind) if item.label == label)


def click(at, label):
    """Click a labeled button, rerun the app, and check for errors."""
    widget(at, "button", label).click().run()
    assert not at.exception


def add_pet(at, name, species="dog"):
    """Fill and submit the Add pet form."""
    widget(at, "text_input", "Pet name").set_value(name)
    widget(at, "selectbox", "Species").set_value(species)
    click(at, "Add pet")


def add_task(at, pet, title, minutes, priority, time=""):
    """Fill and submit the Add task form for a selected pet."""
    widget(at, "selectbox", "Pet").set_value(pet)
    widget(at, "text_input", "Task title").set_value(title)
    widget(at, "number_input", "Duration (minutes)").set_value(minutes)
    widget(at, "selectbox", "Priority").set_value(priority)
    widget(at, "text_input", "Preferred time (HH:MM, optional)").set_value(time)
    click(at, "Add task")


def test_add_pet_creates_pet_object_that_persists():
    """Check a pet is stored as a Pet object across app reruns."""
    at = start_app()
    add_pet(at, "Biscuit")

    at.run()

    pets = at.session_state.owner.pets
    assert [pet.name for pet in pets] == ["Biscuit"]
    assert type(pets[0]).__name__ == "Pet"


def test_duplicate_pet_name_is_rejected():
    """Check adding a duplicate pet name shows an error and keeps one pet."""
    at = start_app()
    add_pet(at, "Mochi", "cat")
    add_pet(at, "Mochi", "cat")

    assert len(at.session_state.owner.pets) == 1
    assert at.error


def test_add_task_goes_to_selected_pet():
    """Check a task is added only to the selected pet."""
    at = start_app()
    add_pet(at, "Biscuit")
    add_pet(at, "Mochi", "cat")
    add_task(at, "Mochi", "Give meds", 5, "high", "08:10")

    pets = {pet.name: pet for pet in at.session_state.owner.pets}
    assert [task.title for task in pets["Mochi"].tasks] == ["Give meds"]
    assert pets["Biscuit"].tasks == []


def test_bad_time_is_rejected_without_crashing():
    """Check an invalid preferred time shows an error and adds no task."""
    at = start_app()
    add_pet(at, "Biscuit")
    add_task(at, "Biscuit", "Walk", 30, "high", "8am")

    assert at.session_state.owner.get_pet("Biscuit").tasks == []
    assert at.error


def test_generate_schedule_skips_and_warns():
    """Check schedule output includes tasks, a skipped task, and a conflict."""
    at = start_app()
    add_pet(at, "Biscuit")
    add_pet(at, "Mochi", "cat")
    add_task(at, "Biscuit", "Morning walk", 30, "high", "08:00")
    add_task(at, "Mochi", "Give meds", 5, "high", "08:10")
    add_task(at, "Biscuit", "Fetch", 20, "low")

    widget(at, "number_input", "Minutes available today").set_value(40)
    click(at, "Save owner")
    click(at, "Generate schedule")

    rendered = "\n".join(
        str(element.value)
        for kind in ("info", "warning", "markdown", "text", "table", "dataframe")
        for element in getattr(at, kind)
    )
    for expected in ("Morning walk", "Give meds", "Skipped", "Fetch", "overlaps"):
        assert expected in rendered


def test_task_list_is_sorted_by_time_and_filtered():
    """Check task list ordering and pet filtering in the Streamlit UI."""
    at = start_app()
    add_pet(at, "Biscuit")
    add_pet(at, "Mochi", "cat")
    add_task(at, "Biscuit", "Dinner", 10, "medium", "18:00")
    add_task(at, "Mochi", "Meds", 5, "high", "09:00")
    add_task(at, "Biscuit", "Walk", 30, "high", "07:30")

    assert list(at.table[-1].value["Task"]) == ["Walk", "Meds", "Dinner"]

    widget(at, "selectbox", "Show tasks for").set_value("Biscuit")
    at.run()

    assert list(at.table[-1].value["Task"]) == ["Walk", "Dinner"]


def test_mark_complete_creates_next_occurrence():
    """Check completing a task creates a pending daily occurrence."""
    at = start_app()
    add_pet(at, "Biscuit")
    add_task(at, "Biscuit", "Walk", 30, "high")
    today = at.session_state.owner.get_pet("Biscuit").tasks[0].due_date

    click(at, "Mark complete")

    tasks = at.session_state.owner.get_pet("Biscuit").tasks
    assert [task.completed for task in tasks] == [True, False]
    assert tasks[1].due_date == today + timedelta(days=1)
    assert any("Next one (daily) is due" in str(message.value) for message in at.success)


def test_schedule_without_conflicts_says_so():
    """Show a success message and no warning for a conflict-free schedule."""
    at = start_app()
    add_pet(at, "Biscuit")
    add_task(at, "Biscuit", "Walk", 30, "high")

    click(at, "Generate schedule")

    assert any("No time conflicts" in str(message.value) for message in at.success)
    assert len(at.warning) == 0
