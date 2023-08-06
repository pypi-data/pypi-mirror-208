"""Tools for planning and scheduling analysis."""

from statistics import mean
from typing import Callable, Union

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node
from serde import asdict, from_dict

from raplan.classes import (
    Component,
    Horizon,
    Maintenance,
    Project,
    Schedule,
    ScheduleItem,
    System,
    Task,
)

NUMBERS = {int, float, Union[int, float]}
CLASSES = Union[
    Component,
    Horizon,
    Maintenance,
    Project,
    Schedule,
    ScheduleItem,
    System,
    Task,
]


class ClassToKind:
    """Class to Kind conversion."""

    COMPONENT = "component"
    HORIZON = "horizon"
    MAINTENANCE = "maintenance"
    PROJECT = "project"
    SCHEDULE = "schedule"
    SCHEDULEITEM = "schedule_item"
    SYSTEM = "system"
    TASK = "task"


class KindToClass:
    """Kind to Class conversion."""

    COMPONENT = Component
    HORIZON = Horizon
    MAINTENANCE = Maintenance
    PROJECT = Project
    SCHEDULE = Schedule
    SCHEDULE_ITEM = ScheduleItem
    SYSTEM = System
    TASK = Task


def _to_node(obj: CLASSES) -> Node:
    """Convert any of the classes to a Node."""
    # Use asdict to store serialized data to support later recreation.
    name = getattr(obj, "name", None)
    uuid = getattr(obj, "uuid", None)
    if name is None:
        node_name = uuid
    elif uuid is None:
        node_name = name
    else:
        node_name = f"{uuid}.{name}"
    node = Node(
        name=node_name,
        uuid=uuid,
        labels=[] if name is None else [name],
        kind=getattr(ClassToKind, obj.__class__.__name__.upper()),
        annotations=dict(data=asdict(obj)),
    )
    node._weights = dict()  # Hard set to empty.
    for f in obj.__dataclass_fields__.values():
        if f.type in NUMBERS:
            node.weights[f.name] = getattr(obj, f.name)
    return node


def _from_node(node: Node) -> CLASSES:
    """Convert node back into class."""
    cls = getattr(KindToClass, node.kind.upper())
    obj = from_dict(cls, node.annotations.data)
    for k, v in node.weights.items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    return obj


def get_maintenance_graph(project: Project, threshold: Union[int, float]) -> Graph:
    """Get a graph of maintenance tasks. Edges are generated with an adjacency value of
    of the threshold minus the time difference between tasks.

    Arguments:
        project: Scheduling project to generate a graph for.
        threshold: Maximum time difference. Tasks that are within this threshold will be
            assigned an adjacency edge.

    Returns:
        Graph of maintenance tasks.
    """
    graph = Graph(
        labels=[project.name] if project.name else [],
        kind=ClassToKind.PROJECT,
        annotations=dict(data=asdict(project)),
    )

    maintenance_nodes: list[Node] = []
    for system in project.systems:
        if system.uuid in graph.node_uuid_dict:
            s = graph[system.uuid]
        else:
            s = _to_node(system)
            graph.add_node(s)

        for component in system.components:
            if component.uuid in graph.node_uuid_dict:
                c = graph[component.uuid]
            else:
                c = _to_node(component)
                graph.add_node(c)

            graph.add_edge(Edge(source=c, target=s, kind="belongs_to"))
            graph.add_edge(Edge(source=s, target=c, kind="consists_of"))

            for maintenance in component.maintenance:
                if maintenance.uuid in graph.node_uuid_dict:
                    m = graph[maintenance.uuid]
                else:
                    m = _to_node(maintenance)
                    graph.add_node(m)

                # Add edges to both component and system.
                graph.add_edge(Edge(source=m, target=c, kind="maintenance"))
                graph.add_edge(Edge(source=c, target=m, kind="maintenance"))
                graph.add_edge(Edge(source=m, target=s, kind="maintenance"))
                graph.add_edge(Edge(source=s, target=m, kind="maintenance"))

                for mx in maintenance_nodes:
                    delta_t = abs(m.weights["time"] - mx.weights["time"])
                    if not (delta_t < threshold):
                        continue
                    weight = 1.0 / (delta_t + 1.0)

                    graph.add_edge(
                        Edge(
                            source=m,
                            target=mx,
                            kind="adjacency",
                            weights=dict(adjacency=weight),
                        )
                    )
                    graph.add_edge(
                        Edge(
                            source=mx,
                            target=m,
                            kind="adjacency",
                            weights=dict(adjacency=weight),
                        )
                    )

                maintenance_nodes.append(m)

    return graph


def project_from_graph(graph: Graph) -> Project:
    """Recreate a Project from a Graph. Utilizes the 'data' annotation to build base
    objects, and overrides it with data found in the graph constructs.

    Arguments:
        graph: Graph data.
    """
    project = _from_node(graph)  # It works, even though naming is odd.
    assert isinstance(project, Project)

    systems = []
    for s in filter(lambda n: n.kind == "system" and n.is_leaf, graph.nodes):
        system = _from_node(s)
        assert isinstance(system, System)

        components: list[Component] = []
        for ec in graph.edges_from(s):
            if ec.kind != "consists_of" or ec.target.kind != "component" or not ec.target.is_leaf:
                continue
            c = ec.target

            component = _from_node(c)
            assert isinstance(component, Component)

            maintenance: list[Maintenance] = []
            for em in graph.edges_from(c):
                if (
                    em.kind != "maintenance"
                    or em.target.kind != "maintenance"
                    or not em.target.is_leaf
                ):
                    continue
                m = em.target

                maintenance_item = _from_node(m)
                assert isinstance(maintenance_item, Maintenance)
                maintenance.append(maintenance_item)

            component.maintenance = maintenance
            components.append(component)

        system.components = components
        systems.append(system)

    project.systems = systems
    return project


def _sync_start_earliest(nodes: list[Node]) -> list[Union[int, float]]:
    min_start = min(getattr(_from_node(n), "time", 0) for n in nodes)
    return len(nodes) * [min_start]


def _sync_start_latest(nodes: list[Node]) -> list[Union[int, float]]:
    max_start = max(getattr(_from_node(n), "time", 0) for n in nodes)
    return len(nodes) * [max_start]


def _sync_start_mean(nodes: list[Node]) -> list[Union[int, float]]:
    mean_start = mean(getattr(_from_node(n), "time", 0) for n in nodes)
    return len(nodes) * [mean_start]


def _get_end(n: Node) -> Union[int, float]:
    return getattr(_from_node(n), "end", 0)  # Maintenance


def _get_start_from_end(n: Node, end: Union[int, float]) -> Union[int, float]:
    m = _from_node(n)
    assert isinstance(m, Maintenance)
    return end - m.task.duration


def _sync_end_earliest(nodes: list[Node]) -> list[Union[int, float]]:
    min_end = min(_get_end(n) for n in nodes)
    return [_get_start_from_end(n, min_end) for n in nodes]


def _sync_end_latest(nodes: list[Node]) -> list[Union[int, float]]:
    max_end = max(_get_end(n) for n in nodes)
    return [_get_start_from_end(n, max_end) for n in nodes]


def _sync_end_mean(nodes: list[Node]) -> list[Union[int, float]]:
    mean_end = mean(_get_end(n) for n in nodes)
    return [_get_start_from_end(n, mean_end) for n in nodes]


SCHEDULE_FN = dict(
    SYNC_START_EARLIEST=_sync_start_earliest,
    SYNC_START_LATEST=_sync_start_latest,
    SYNC_START_MEAN=_sync_start_mean,
    SYNC_END_EARLIEST=_sync_end_earliest,
    SYNC_END_LATEST=_sync_end_latest,
    SYNC_END_MEAN=_sync_end_mean,
)
"""Maintenance task scheduling functions."""


def process_clustered_maintenance(
    graph: Graph,
    schedule_fn: Callable[[list[Node]], list[Union[int, float]]] = SCHEDULE_FN[
        "SYNC_START_EARLIEST"
    ],
):
    """Check for maintenance nodes with parents and synchronize their times.

    Arguments:
        graph: Maintenance graph.
        schedule_fn: A method that takes a list of (maintenance) nodes and returns a new
            list with modified starting times to incorporate. It should not modify the
            nodes in-place.
    """
    for n in graph.nodes:
        if n.kind != "maintenance" or n.is_leaf:
            continue
        leafs = n.children
        times = schedule_fn(leafs)
        for i, time in enumerate(times):
            leaf = leafs[i]
            leaf.weights["time"] = time
            leaf.annotations.data["time"] = time
