"""Dataclasses to use and configure planning and scheduling with."""

from dataclasses import dataclass
from typing import Optional, Union
from uuid import UUID, uuid4

from serde import InternalTagging, field, serde

from raplan import distributions

__all__ = [
    "Task",
    "Maintenance",
    "Component",
    "System",
    "Horizon",
    "Procedure",
    "Project",
    "ScheduleItem",
    "Schedule",
    "Procedure",
    "CyclicStrategy",
]


def _is_empty(lst: Union[list, dict, set]) -> bool:
    """Check whether a list is empty."""
    return len(lst) == 0


@serde(tagging=InternalTagging("type"))
@dataclass
class Task:
    """Maintenance task to apply to a component.

    Arguments:
        name: Name for this action.
        rejuvenation: Rejuvenation factor between [0.0-1.0]. Percentage of age that is
            regained. Therefore, 1.0 would mean a full replacement.
        duration: Duration of the maintenance. Usually in years.
        cost: Cost of the maintenance. Usually expressed in a currency or equivalent.
    """

    name: Optional[str] = field(default=None, skip_if_default=True)
    rejuvenation: Union[int, float] = 1.0
    duration: Union[int, float] = 1.0
    cost: Union[int, float] = 1.0
    uuid: UUID = field(default_factory=uuid4)


@serde(tagging=InternalTagging("type"))
@dataclass
class Maintenance:
    """Maintenance task scheduled at a point in time.

    Arguments:
        name: Name of this maintenance task.
        task: Task information.
        time: Time at which this maintenance is scheduled.
    """

    name: Optional[str] = field(default=None, skip_if_default=True)
    task: Task = field(default_factory=Task)
    time: Union[int, float] = 1.0
    uuid: UUID = field(default_factory=uuid4)

    @property
    def end(self) -> Union[int, float]:
        """End time of this maintenance."""
        return self.time + self.task.duration


@serde(tagging=InternalTagging("type"))
@dataclass
class Component:
    """Component with a failure distribution.

    Arguments:
        name: Name of this component.
        age: Starting age offset (usually in years).
        distribution: Failure distribution to use.
        maintenance: List of maintenance tasks that should be applied over this
            component's lifespan.
    """

    name: Optional[str] = field(default=None, skip_if_default=True)
    age: Union[int, float] = 0.0
    lifetime: Union[int, float] = 1.0
    distribution: distributions.Distributions = field(default_factory=distributions.Weibull)
    maintenance: list[Maintenance] = field(default_factory=list, skip_if=_is_empty, repr=False)
    uuid: UUID = field(default_factory=uuid4)

    def get_ordered_maintenance(self) -> list[Maintenance]:
        """Maintenance tasks sorted in time."""
        return sorted(self.maintenance, key=lambda m: m.time)

    def cfp(self, x: Union[int, float] = 1.0) -> float:
        """Cumulative failure probability density function incorporating maintenance."""
        return self.distribution.cdf(self.get_age_at(x))

    def get_age_at(self, x: Union[int, float] = 1.0) -> float:
        """Effective age at a point in time given the currently set schedule."""
        age = float(self.age)
        last_time = 0.0
        for m in self.get_ordered_maintenance():
            if m.time > x:
                # Maintenance is yet to happen.
                break
            # Apply rejuvenation with the then actual age.
            age = (age + m.time - last_time) * (1.0 - m.task.rejuvenation)
            last_time = m.time
        # Add remaining time since last maintenance.
        age += x - last_time
        return age

    def schedule_maintenance(self, maintenance: Maintenance):
        """Schedule maintenance for a single or all system's component or all
        components.

        Arguments:
            maintenance: Maintenance to schedule.
        """
        self.maintenance.append(maintenance)


@serde(tagging=InternalTagging("type"))
@dataclass
class System:
    """A system consisting of multiple components.

    Arguments:
        name: Name of this system.
        components: Components of this system.
    """

    name: Optional[str] = field(default=None, skip_if_default=True)
    components: list[Component] = field(default_factory=list, skip_if=_is_empty, repr=False)
    uuid: UUID = field(default_factory=uuid4)

    def cfp(self, x: Union[int, float] = 1.0) -> float:
        """Cumulative failure probability density function as the sum of its
        components' respective function incorporating maintenance.
        """
        if len(self.components):
            return distributions.compound_probability(c.cfp(x) for c in self.components)
        else:
            return 0.0

    def get_ordered_maintenance(self) -> list[Maintenance]:
        """Get all maintenance ordered in time."""
        return sorted([m for c in self.components for m in c.maintenance], key=lambda m: m.time)

    def get_component(self, name: str) -> Component:
        """Get a component by name."""
        for c in self.components:
            if c.name == name:
                return c
        raise KeyError(f"Component with name '{name}' does not exist in this system.")

    def schedule_maintenance(self, maintenance: Maintenance, component: Optional[str] = None):
        """Schedule maintenance for a single or all system's component or all
        components.

        Arguments:
            maintenance: Maintenance to schedule.
            component: Component name. If kept `None`, it will be applied to all.
        """
        if component is None:
            for c in self.components:
                c.schedule_maintenance(maintenance)
        else:
            self.get_component(component).schedule_maintenance(maintenance)


@serde(tagging=InternalTagging("type"))
@dataclass
class Horizon:
    """Planning and scheduling horizon.

    Arguments:
        start: Start of the planning horizon.
        end: End of the planning horizon. Optional, as it is otherwise derived from the
            final task in the schedule.
    """

    start: Union[int, float] = 0.0
    end: Optional[Union[int, float]] = field(default=None, skip_if_default=True)
    uuid: UUID = field(default_factory=uuid4)

    def get_range(self, steps: int, zero_based: bool = True) -> list[Union[int, float]]:
        """Range between start and end (inclusive) in the given number of steps."""
        if self.end is None:
            raise ValueError("Can't calculate a range with no horizon end value.")
        step_size = (self.end - self.start) / steps
        start = type(self.start)(0) if zero_based else self.start
        return [start + i * step_size for i in range(steps + 1)]


@serde(tagging=InternalTagging("type"))
@dataclass
class Project:
    """Planning and scheduling project."""

    name: Optional[str] = field(default=None, skip_if_default=True)
    horizon: Horizon = field(default_factory=Horizon)
    systems: list[System] = field(default_factory=list, skip_if=_is_empty, repr=False)
    uuid: UUID = field(default_factory=uuid4)

    def get_horizon_end(self) -> float:
        """Get the end of the planning horizon or last maintenance task."""
        if self.horizon.end is None:
            end = 0.0
            try:
                end = max(m.time for s in self.systems for c in s.components for m in c.maintenance)
            except ValueError:
                pass  # arg is an empty sequency: end = 0.0
            finally:
                return end
        return self.horizon.end

    def cfp(self, x: Union[int, float] = 1.0) -> float:
        """Cumulative failure probability density function as the sum of its
        systems' respective function incorporating maintenance.
        """
        if len(self.systems):
            return distributions.compound_probability(s.cfp(x) for s in self.systems)
        else:
            return 0.0

    def get_ordered_maintenance(self) -> list[Maintenance]:
        """Get all maintenance ordered in time."""
        return sorted(
            [m for s in self.systems for c in s.components for m in c.maintenance],
            key=lambda m: m.time,
        )

    def get_system(self, name: str) -> System:
        """Get a component by name."""
        for s in self.systems:
            if s.name == name:
                return s
        raise KeyError(f"System with name '{name}' does not exist in this project.")

    def schedule_maintenance(
        self,
        maintenance: Maintenance,
        system: Optional[str] = None,
        component: Optional[str] = None,
    ):
        """Schedule maintenance for a single or all system's component or all
        components.

        Arguments:
            maintenance: Maintenance to schedule.
            system: System name. If kept `None`, it will be applied to all.
            component: Component name. If kept `None`, it will be applied to all.
        """
        if system is None:
            for s in self.systems:
                s.schedule_maintenance(maintenance, component=component)
        else:
            self.get_system(system).schedule_maintenance(maintenance, component=component)

    def get_schedule(self) -> "Schedule":
        """Get a fully generated schedule."""
        return Schedule(
            items=[
                ScheduleItem(
                    name=m.task.name,
                    project=self.name,
                    system=s.name,
                    component=c.name,
                    maintenance=m.name,
                    task=m.task.name,
                    rejuvenation=m.task.rejuvenation,
                    duration=m.task.duration,
                    cost=m.task.cost,
                    time=m.time,
                )
                for s in self.systems
                for c in s.components
                for m in c.maintenance
            ]
        )


@serde(tagging=InternalTagging("type"))
@dataclass
class ScheduleItem:
    """A schedule item with full detail regarding its system, component and maintenance
    task info.

    Arguments:
        name: Name for this action. rejuvenation: Rejuvenation factor between [0.0-1.0].
        Percentage of age that is
            regained. Therefore, 1.0 would mean a full replacement.
        duration: Duration of the maintenance. Usually in years. cost: Cost of the
        maintenance. Usually expressed in a currency or equivalent. system: Name of the
        system to which this maintenance is applied. component: Name of the component to
        which this maintenance is applied. time: Time at which this maintenance is
        scheduled.
    """

    name: Optional[str] = field(default=None, skip_if_default=True)
    project: Optional[str] = field(default=None, skip_if_default=True)
    system: Optional[str] = field(default=None, skip_if_default=True)
    component: Optional[str] = field(default=None, skip_if_default=True)
    maintenance: Optional[str] = field(default=None, skip_if_default=True)
    task: Optional[str] = field(default=None, skip_if_default=True)
    rejuvenation: Union[int, float] = 1.0
    duration: Union[int, float] = 1.0
    cost: Union[int, float] = 1.0
    time: Union[int, float] = 1.0
    uuid: UUID = field(default_factory=uuid4)


@serde(tagging=InternalTagging("type"))
@dataclass
class Schedule:
    """A full maintenance schedule.

    Arguments:
        items: Scheduled tasks.
    """

    items: list[ScheduleItem] = field(default_factory=list, skip_if=_is_empty)

    def get_ordered_maintenance(self) -> list[ScheduleItem]:
        """Get all tasks ordered in time."""
        return sorted(self.items, key=lambda t: t.time)

    @classmethod
    def from_projects(cls, projects: list[Project]) -> "Schedule":
        """Create a schedule for multiple projects."""

        schedules = [p.get_schedule() for p in projects]
        return cls(items=[i for s in schedules for i in s.items])


@serde(tagging=InternalTagging("type"))
@dataclass
class Procedure:
    """A specific grouping of tasks to apply to a System.

    Note:
        Mainly used for plotting purposes.

    Arguments:
        name: Name for this procedure.
        system: System (name) to which the procedure should be applied.
        kind: Kind of procedure (category name).
        time: Time at which the procedure is scheduled.
        cost: Cost of the procedure.
        duration: Duration of the procedure.
    """

    name: Optional[str] = field(default=None, skip_if_default=True)
    system: str = "system"
    kind: str = "procedure"
    time: Union[int, float] = 1.0
    cost: Union[int, float] = 1.0
    duration: Union[int, float] = 1.0
    uuid: UUID = field(default_factory=uuid4)


@serde(tagging=InternalTagging("type"))
@dataclass
class CyclicStrategy:
    """Maintenance strategy to renovate or replace a component at certain percentages
    of a cycle.
    """

    tasks: list[Task] = field(default_factory=list, skip_if=_is_empty)
    percentages: list[float] = field(default_factory=list, skip_if=_is_empty)

    def apply_to_component(
        self,
        component: Component,
        cycle_length: Union[int, float],
        horizon: Horizon,
        repeat: bool = True,
        include_history: bool = True,
        integers: bool = False,
        overwrite: bool = True,
    ) -> None:
        """Apply this strategy to a component.

        Arguments:
            component: Component for which to schedule maintenance.
            cycle_length: Cycle length.
            horizon: Planning horizon to consider.
            repeat: Whether the cycle should be repeated until the end of the horizon.
            include_history: Whether to include historical maintenance entries for
                components that have a pre-defined age.
            overwrite: Whether to fully overwrite a component's maintenance planning
                with this new one or extend it.
            integers: Whether to force all times to be integers.
        """
        maintenance = self.get_maintenance(
            component.age,
            cycle_length,
            horizon,
            repeat=repeat,
            include_history=include_history,
            integers=integers,
        )
        if overwrite:
            component.maintenance = maintenance
        else:
            component.maintenance.extend(maintenance)

    def get_maintenance(
        self,
        age: Union[int, float],
        cycle_length: Union[int, float],
        horizon: Horizon,
        repeat: bool = True,
        include_history: bool = True,
        integers: bool = False,
    ) -> list[Maintenance]:
        """Get maintenance list for this strategy.

        Arguments:
            age: Starting age of a virtual component.
            cycle_length: Cycle length.
            horizon: Planning horizon to consider.
            repeat: Whether the cycle should be repeated until the end of the horizon.
            include_history: Whether to include historical maintenance entries for
                components that have a pre-defined age.
            overwrite: Whether to fully overwrite a component's maintenance planning
                with this new one or extend it.
            integers: Whether to force all times to be integers.

        Returns:
            Maintenance list.
        """
        assert len(self.tasks) == len(
            self.percentages
        ), "The number of tasks and percentages should be equal."

        start: Union[int, float] = -age
        end = horizon.end - horizon.start if horizon.end else cycle_length

        offsets = [p * cycle_length for p in self.percentages]
        tasks = sorted(zip(offsets, self.tasks), key=lambda x: x[0])

        maintenance = []
        cycles_offset: Union[int, float] = 0
        while start + cycles_offset < end:
            for offset, task in tasks:
                time = offset + cycles_offset + start
                if integers:
                    time = round(time)

                # No further planning beyond this point.
                if time > end:
                    break

                if not include_history and time < 0:
                    continue

                maintenance.append(
                    Maintenance(
                        f"{task.name} {time}",
                        task=task,
                        time=time,
                    )
                )

            # No further planning beyond this point.
            if not repeat or time > end:
                break

            cycles_offset = cycles_offset + cycle_length

        return maintenance
