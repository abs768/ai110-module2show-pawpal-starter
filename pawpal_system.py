"""Skeletons generated from the PawPal+ UML diagram."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta


PRIORITY_RANKS = {"high": 3, "medium": 2, "low": 1}
END_OF_DAY = 24 * 60
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


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
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return this task's priority rank."""
        return PRIORITY_RANKS.get(self.priority.lower(), 0)

    def next_occurrence(self) -> Task | None:
        """Return the next incomplete occurrence for supported frequencies."""
        days = RECURRENCE_DAYS.get(self.frequency.lower())
        if days is None:
            return None
        return replace(
            self,
            completed=False,
            due_date=self.due_date + timedelta(days=days),
        )


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

    def get_all_tasks(self, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Collect task pairs across pets, optionally including completed tasks."""
        return [
            (pet, task)
            for pet in self.pets
            for task in (pet.tasks if include_completed else pet.get_pending_tasks())
        ]


@dataclass
class ScheduledTask:
    task: Task
    pet_name: str
    start_time: str
    end_time: str
    reason: str = ""


class Scheduler:
    def __init__(self, owner: Owner, day: date | None = None) -> None:
        """Create a scheduler for an owner."""
        self.owner = owner
        self.day = day or date.today()
        self.skipped: list[tuple[Pet, Task, str]] = []

    def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
        """Complete a task and add its next recurring occurrence when available."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

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
        task_pairs = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.due_date <= self.day
        ]
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
                start_minutes = to_minutes(task.preferred_time)
                if start_minutes + task.duration_minutes > END_OF_DAY:
                    self.skipped.append((pet, task, "would run past midnight"))
                    continue
                plan.append(
                    self._make_slot(
                        pet,
                        task,
                        start_minutes,
                        f"{task.priority.lower()} priority; fixed at {task.preferred_time}",
                    )
                )
            else:
                remaining.append((pet, task))

        for pet, task in remaining:
            start_minutes = self._earliest_free_start(plan, task.duration_minutes)
            if start_minutes + task.duration_minutes > END_OF_DAY:
                self.skipped.append((pet, task, "would run past midnight"))
                continue
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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred time, placing tasks without one last."""
        return sorted(
            tasks,
            key=lambda task: to_minutes(task.preferred_time)
            if task.preferred_time
            else END_OF_DAY,
        )

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Filter all owner tasks by pet name and completion status."""
        task_pairs = self.owner.get_all_tasks(include_completed=True)
        return [
            (pet, task)
            for pet, task in task_pairs
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def fits_in_time(self, task: Task, minutes_left: int) -> bool:
        """Check whether a task fits the remaining time."""
        return task.duration_minutes <= minutes_left

    def detect_conflicts(self, plan: list[ScheduledTask]) -> list[str]:
        """Find every overlapping pair of scheduled tasks."""
        ordered = sorted(plan, key=lambda slot: to_minutes(slot.start_time))
        conflicts: list[str] = []
        for i, first in enumerate(ordered):
            first_end = to_minutes(first.end_time)

            for second in ordered[i + 1 :]:
                second_start = to_minutes(second.start_time)
                if second_start >= first_end:
                    break

                pet_label = (
                    "[same pet]"
                    if first.pet_name == second.pet_name
                    else "[different pets]"
                )
                conflicts.append(
                    f"'{first.task.title}' for {first.pet_name} "
                    f"({first.start_time}-{first.end_time}) overlaps "
                    f"'{second.task.title}' for {second.pet_name} "
                    f"({second.start_time}-{second.end_time}) {pet_label}"
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
