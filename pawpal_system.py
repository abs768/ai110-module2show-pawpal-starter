"""Skeletons generated from the PawPal+ UML diagram."""

from __future__ import annotations

from dataclasses import dataclass, field


PRIORITY_RANKS = {"high": 3, "medium": 2, "low": 1}


def to_minutes(time_text: str) -> int:
    """Convert an HH:MM time to minutes after midnight."""
    hours_text, minutes_text = time_text.split(":")
    return int(hours_text) * 60 + int(minutes_text)


def to_hhmm(minutes: int) -> str:
    """Format minutes after midnight as HH:MM."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "general"
    preferred_time: str | None = None
    frequency: str = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return this task's priority rank."""
        return PRIORITY_RANKS.get(self.priority.lower(), 0)


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        for index, task in enumerate(self.tasks):
            if task.title == title:
                del self.tasks[index]
                break

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's pending tasks."""
        return [task for task in self.tasks if task.completed is False]


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    day_start: str = "08:00"
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name."""
        self.pets = [pet for pet in self.pets if pet.name != name]

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name."""
        return next((pet for pet in self.pets if pet.name == name), None)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect (pet, task) pairs for all pending tasks across pets."""
        return [
            (pet, task)
            for pet in self.pets
            for task in pet.get_pending_tasks()
        ]


@dataclass
class ScheduledTask:
    task: Task
    pet_name: str
    start_time: str
    end_time: str
    reason: str = ""


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for an owner."""
        self.owner = owner
        self.skipped: list[tuple[Pet, Task, str]] = []

    def _sort_key(self, task: Task) -> tuple[int, int, int]:
        """Build the task ordering key for priority, preferred time, and duration."""
        preferred_minutes = (
            to_minutes(task.preferred_time)
            if task.preferred_time is not None
            else 1440
        )
        return (-task.priority_rank(), preferred_minutes, task.duration_minutes)

    def _make_slot(
        self, pet: Pet, task: Task, start_minutes: int, placement: str
    ) -> ScheduledTask:
        """Create a scheduled slot for a pet's task."""
        return ScheduledTask(
            task=task,
            pet_name=pet.name,
            start_time=to_hhmm(start_minutes),
            end_time=to_hhmm(start_minutes + task.duration_minutes),
            reason=placement,
        )

    def _earliest_free_start(
        self, plan: list[ScheduledTask], duration: int
    ) -> int:
        """Find the earliest gap of the requested duration from day start."""
        cursor = to_minutes(self.owner.day_start)
        for slot in sorted(plan, key=lambda item: to_minutes(item.start_time)):
            slot_start = to_minutes(slot.start_time)
            slot_end = to_minutes(slot.end_time)
            if cursor + duration <= slot_start:
                return cursor
            if cursor < slot_end:
                cursor = slot_end
        return cursor

    def generate_plan(self) -> list[ScheduledTask]:
        """Generate a daily care plan."""
        self.skipped = []
        task_pairs = self.owner.get_all_tasks()
        ordered_pairs = sorted(task_pairs, key=lambda pair: self._sort_key(pair[1]))

        minutes_left = self.owner.available_minutes
        chosen: list[tuple[Pet, Task]] = []
        for pet, task in ordered_pairs:
            if self.fits_in_time(task, minutes_left):
                chosen.append((pet, task))
                minutes_left -= task.duration_minutes
            else:
                reason = (
                    f"needs {task.duration_minutes} min, only {minutes_left} min left"
                )
                self.skipped.append((pet, task, reason))

        plan: list[ScheduledTask] = []
        remaining: list[tuple[Pet, Task]] = []
        for pet, task in chosen:
            if task.preferred_time is not None:
                plan.append(
                    self._make_slot(
                        pet,
                        task,
                        to_minutes(task.preferred_time),
                        f"{task.priority.lower()} priority; fixed at {task.preferred_time}",
                    )
                )
            else:
                remaining.append((pet, task))

        for pet, task in remaining:
            start_minutes = self._earliest_free_start(plan, task.duration_minutes)
            plan.append(
                self._make_slot(
                    pet,
                    task,
                    start_minutes,
                    f"{task.priority.lower()} priority; placed in earliest free slot",
                )
            )

        return sorted(plan, key=lambda slot: to_minutes(slot.start_time))

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority."""
        return sorted(tasks, key=self._sort_key)

    def fits_in_time(self, task: Task, minutes_left: int) -> bool:
        """Check whether a task fits the remaining time."""
        return task.duration_minutes <= minutes_left

    def detect_conflicts(self, plan: list[ScheduledTask]) -> list[str]:
        """Find conflicts in a plan."""
        ordered_plan = sorted(plan, key=lambda slot: to_minutes(slot.start_time))
        conflicts: list[str] = []
        for previous, following in zip(ordered_plan, ordered_plan[1:]):
            if to_minutes(following.start_time) < to_minutes(previous.end_time):
                conflicts.append(
                    f"'{previous.task.title}' for {previous.pet_name} "
                    f"({previous.start_time}-{previous.end_time}) overlaps "
                    f"'{following.task.title}' for {following.pet_name} "
                    f"({following.start_time}-{following.end_time})"
                )
        return conflicts

    def explain_plan(self, plan: list[ScheduledTask]) -> str:
        """Explain the decisions in a plan."""
        used_minutes = sum(slot.task.duration_minutes for slot in plan)
        lines = [
            f"Scheduled {len(plan)} task(s) using {used_minutes} of "
            f"{self.owner.available_minutes} available minutes.",
            "Sort rule: (high > medium > low), then preferred time, then shortest first",
        ]
        lines.extend(
            f"Skipped '{task.title}' for {pet.name}: {reason}."
            for pet, task, reason in self.skipped
        )
        lines.extend(
            f"Conflict: {conflict}"
            for conflict in self.detect_conflicts(plan)
        )
        return "\n".join(lines)
