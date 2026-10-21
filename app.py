import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, to_minutes


def valid_time(text: str) -> bool:
    """Return whether text is a valid 24-hour HH:MM time."""
    try:
        hours_text, minutes_text = text.split(":")
        if (
            len(hours_text) != 2
            or len(minutes_text) != 2
            or not hours_text.isdigit()
            or not minutes_text.isdigit()
        ):
            return False
        hours = int(hours_text)
        minutes = int(minutes_text)
        to_minutes(text)
        return 0 <= hours < 24 and 0 <= minutes < 60
    except (AttributeError, ValueError):
        return False


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan daily pet care around the time you have today.")

# Streamlit reruns this script from the top on every click, so keep the owner in session state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
owner = st.session_state.owner

st.header("👤 Owner")
with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value=owner.name)
    available_minutes = st.number_input(
        "Minutes available today",
        min_value=0,
        max_value=1440,
        value=owner.available_minutes,
        step=5,
    )
    day_start = st.text_input("Day start (HH:MM)", value=owner.day_start)
    save_owner = st.form_submit_button("Save owner")

if save_owner:
    if not valid_time(day_start):
        st.error("Enter a valid day start time in HH:MM format.")
    else:
        owner.name = owner_name.strip()
        owner.available_minutes = int(available_minutes)
        owner.day_start = day_start
        st.success("Owner information saved.")

st.header("🐶 Pets")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed")
    age = st.number_input("Age", min_value=0, max_value=100, value=0, step=1)
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    cleaned_pet_name = pet_name.strip()
    if not cleaned_pet_name:
        st.error("Enter a pet name.")
    elif owner.get_pet(cleaned_pet_name) is not None:
        st.error(f"A pet named {cleaned_pet_name} already exists.")
    else:
        owner.add_pet(
            Pet(
                name=cleaned_pet_name,
                species=species,
                breed=breed.strip(),
                age=int(age),
            )
        )
        st.success(f"Added {cleaned_pet_name}.")

if owner.pets:
    st.table(
        [
            {
                "Name": pet.name,
                "Species": pet.species,
                "Breed": pet.breed,
                "Age": pet.age,
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet")

st.header("📝 Care tasks")
if not owner.pets:
    st.caption("Add a pet first to enter care tasks.")
else:
    with st.form("task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Pet", [pet.name for pet in owner.pets])
        task_title = st.text_input("Task title")
        duration_minutes = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=15, step=1
        )
        priority = st.selectbox("Priority", ["high", "medium", "low"])
        category = st.selectbox(
            "Category",
            ["walk", "feeding", "meds", "enrichment", "grooming", "general"],
        )
        preferred_time = st.text_input("Preferred time (HH:MM, optional)")
        frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])
        add_task = st.form_submit_button("Add task")

    if add_task:
        cleaned_title = task_title.strip()
        cleaned_time = preferred_time.strip()
        if not cleaned_title:
            st.error("Enter a task title.")
        elif cleaned_time and not valid_time(cleaned_time):
            st.error("Enter a valid preferred time in HH:MM format, or leave it blank.")
        else:
            selected_pet = owner.get_pet(selected_pet_name)
            if selected_pet is None:
                st.error("Select a pet before adding a task.")
            else:
                selected_pet.add_task(
                    Task(
                        title=cleaned_title,
                        duration_minutes=int(duration_minutes),
                        priority=priority,
                        category=category,
                        preferred_time=cleaned_time or None,
                        frequency=frequency,
                    )
                )
                st.success(f"Added {cleaned_title} for {selected_pet.name}.")

    scheduler = Scheduler(owner)
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    st.subheader("Task list")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox("Show tasks for", ["All pets"] + [pet.name for pet in owner.pets])
    with filter_col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Done"])

    selected_pet_name = None if pet_filter == "All pets" else pet_filter
    completed_filter = {"All": None, "Pending": False, "Done": True}[status_filter]
    task_pairs = scheduler.filter_tasks(
        pet_name=selected_pet_name,
        completed=completed_filter,
    )
    time_sorted_tasks = scheduler.sort_by_time([task for _, task in task_pairs])
    pet_by_task_id = {id(task): pet for pet, task in task_pairs}
    task_pairs = [(pet_by_task_id[id(task)], task) for task in time_sorted_tasks]
    st.caption("Sorted by preferred time; tasks with no set time are listed last.")
    if task_pairs:
        st.table(
            [
                {
                    "Time": task.preferred_time or "any",
                    "Pet": pet.name,
                    "Task": task.title,
                    "Min": task.duration_minutes,
                    "Priority": task.priority,
                    "Repeats": task.frequency,
                    "Due": task.due_date.isoformat(),
                    "Status": "✅ done" if task.completed else "pending",
                }
                for pet, task in task_pairs
            ]
        )
    else:
        st.info("No care tasks match these filters.")

    st.subheader("Mark a task done")
    pending_pairs = scheduler.filter_tasks(completed=False)
    if pending_pairs:
        pending_labels = [
            f"{pet.name}: {task.title} (due {task.due_date.isoformat()})"
            for pet, task in pending_pairs
        ]
        selected_pending_index = st.selectbox(
            "Pending task",
            range(len(pending_pairs)),
            format_func=lambda index: pending_labels[index],
        )
        if st.button("Mark complete"):
            pet, task = pending_pairs[selected_pending_index]
            next_task = scheduler.mark_task_complete(pet, task)
            if next_task is None:
                message = f"Marked '{task.title}' done. It doesn't repeat."
            else:
                message = (
                    f"Marked '{task.title}' done. Next one ({task.frequency}) is due "
                    f"{next_task.due_date.isoformat()}."
                )
            st.session_state.flash = message
            st.rerun()
    else:
        st.info("No pending tasks to mark complete.")

st.header("📅 Today's schedule")
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts(plan)

    if plan:
        used_minutes = sum(item.task.duration_minutes for item in plan)
        st.success(
            f"Planned {len(plan)} task(s) using {used_minutes} of "
            f"{owner.available_minutes} available minutes."
        )
    else:
        st.warning("No tasks are scheduled today.")

    if conflicts:
        conflict_bullets = "\n".join(f"- {conflict}" for conflict in conflicts)
        st.warning(
            f"⚠️ {len(conflicts)} time conflict(s). You can't do these at the same time, "
            "so move one task or shorten it:\n\n"
            f"{conflict_bullets}"
        )
    elif plan:
        st.success("No time conflicts. Every task has its own slot.")

    st.table(
        [
            {
                "Time": f"{item.start_time}-{item.end_time}",
                "Pet": item.pet_name,
                "Task": item.task.title,
                "Min": item.task.duration_minutes,
                "Priority": item.task.priority,
                "Why": item.reason,
            }
            for item in plan
        ]
    )

    if scheduler.skipped:
        skipped_bullets = "\n".join(
            f"- Skipped '{task.title}' for {pet.name}: {reason}."
            for pet, task, reason in scheduler.skipped
        )
        st.info(f"Not scheduled today:\n\n{skipped_bullets}")

    with st.expander("Why this plan?"):
        st.text(scheduler.explain_plan(plan))
