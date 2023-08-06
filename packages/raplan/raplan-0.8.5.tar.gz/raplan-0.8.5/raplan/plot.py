"""RaPlan plotting module."""

from dataclasses import dataclass
from typing import Optional, Sequence, Union

from raplan.classes import Component, Horizon, Maintenance, Procedure, Project, System
from raplan.distributions import compound_probability

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:  # pragma: nocover
    raise ImportError("Please install plotting prerequisites by installing the 'plot' extra.")

_BAR_STYLE = dict(
    bargap=0.0,
    bargroupgap=0.1,
    barmode="relative",
)

COLORS = [
    "#0cc0aa",
    "#9f3b60",
    "#95b833",
    "#a93713",
    "#cfb2b0",
    "#355952",
    "#9085e0",
    "#5a4b72",
    "#da73f8",
    "#08a9e5",
    "#e81659",
    "#4ed31b",
    "#90089c",
    "#cfa543",
    "#ed7f61",
    "#167b2b",
    "#f62ef3",
    "#4328e7",
    "#856619",
    "#3444bc",
]


@dataclass
class Compound:
    """A fictive compound of CFP carrying items."""

    subjects: Sequence[Union[Component, System, Project, "Compound"]]
    name: str = "Compound"

    def cfp(self, x: Union[int, float]) -> float:
        return compound_probability(c.cfp(x) for c in self.subjects)

    def get_ordered_maintenance(self) -> list[Maintenance]:
        return sorted(
            [m for s in self.subjects for m in s.get_ordered_maintenance()],
            key=lambda m: m.time,
        )


def get_overview_figure(
    subject: Union[
        Union[Component, System, Project, Compound],
        Sequence[Union[Component, System, Project, Compound]],
    ],
    xs: list[Union[int, float]],
    horizon: Optional[Horizon] = None,
    compound: Optional[str] = None,
    bar_width: str = "unit",
) -> go.Figure:
    """Get an overview figure consisting of a CFP plot, as well as cost and duration
    bar charts.

    Arguments:
        subject: Planning subject(s) with CFP and maintenance tasks.
        xs: Values to calculate the CFP at.
        horizon: Optional horizon to apply. It's start is used as the X-axis offset to
            apply and the end is used to then set the upper bound of the X-axis.
        compound: If not `None`, the title for a compound CFP line.
        bar_width: How to determine widths of bars shown. 'auto' for Plotly defaults or
            'unit' for widths of 1.

    Returns:
        Subplots overview figure.
    """
    fig = make_subplots(3, 1, shared_xaxes=True, x_title="Time")
    subjects = subject if isinstance(subject, list) else [subject]
    x_offset = 0.0 if horizon is None else horizon.start
    for s in subjects:
        fig.add_trace(_get_cfp_trace(s, xs, x_offset=x_offset), row=1, col=1)
    if compound and len(subjects) > 1:
        fig.add_trace(_get_cfp_trace(Compound(subjects, name=compound), xs, x_offset=x_offset))
    for b in _get_barchart(
        Compound(subjects, "Cost"), prop="cost", x_offset=x_offset, bar_width=bar_width
    ):
        fig.add_trace(b, row=2, col=1)
    for b in _get_barchart(
        Compound(subjects, "Duration"),
        prop="duration",
        x_offset=x_offset,
        bar_width=bar_width,
    ):
        fig.add_trace(b, row=3, col=1)

    fig.layout.update(
        yaxis1=dict(title="CFP"),
        yaxis2=dict(title="Cost"),
        yaxis3=dict(title="Duration"),
        **_BAR_STYLE,
    )
    if horizon:
        _update_xaxis_horizon(fig, horizon)
    return fig


def get_cfp_figure(
    subject: Union[
        Union[Component, System, Project, Compound],
        Sequence[Union[Component, System, Project, Compound]],
    ],
    xs: list[Union[int, float]],
    horizon: Optional[Horizon] = None,
    compound: Optional[str] = None,
    thresholds: dict[str, float] = {"5%": 0.05},
) -> go.Figure:
    """Get a figure displaying the CFP or CFPs of the subject(s).

    Arguments:
        subject: Planning object(s) with a CFP method.
        xs: Time values to calculate CFP values at.
        horizon: Optional horizon to apply. It's start is used as the X-axis offset to
            apply and the end is used to then set the upper bound of the X-axis.
        compound: Whether to show a compound CFP line for the subjects given.
        thresholds: Threshold lines to show.

    Returns:
        Plotly figure.
    """
    subjects = subject if isinstance(subject, list) else [subject]
    x_offset = 0 if horizon is None else horizon.start
    cfps = [_get_cfp_trace(s, xs, x_offset=x_offset) for s in subjects]
    if compound and len(subjects) > 1:
        cfps.append(_get_cfp_trace(Compound(subjects, name=compound), xs, x_offset=x_offset))
    threshold_lines = [
        go.Scatter(
            x=[xs[0] + x_offset, xs[-1] + x_offset],
            y=[v, v],
            name=k,
            line=dict(dash="dash", color="crimson"),
            mode="lines",
        )
        for k, v in thresholds.items()
    ]
    fig = go.Figure(
        cfps + threshold_lines,
        layout=dict(xaxis=dict(title="Time"), yaxis=dict(title="CFP")),
    )
    if horizon:
        _update_xaxis_horizon(fig, horizon)
    return fig


def get_cost_figure(
    subject: Union[
        Union[Component, System, Project, Compound],
        Sequence[Union[Component, System, Project, Compound]],
    ],
    horizon: Optional[Horizon],
    bar_width: str = "unit",
) -> go.Figure:
    """Get a cost bar chart figure.

    Arguments:
        subject: Planning object(s) with maintenance tasks with cost attached.
        horizon: Optional horizon to apply. It's start is used as the X-axis offset to
            apply and the end is used to then set the upper bound of the X-axis.
        bar_width: How to determine widths of bars shown. 'auto' for Plotly defaults or
            'unit' for widths of 1.

    Returns:
        Cost bar chart figure.
    """
    x_offset = 0 if horizon is None else horizon.start
    fig = go.Figure(
        _get_barchart(subject, x_offset=x_offset, prop="cost", bar_width=bar_width),
        layout=dict(xaxis=dict(title="Time"), yaxis=dict(title="Cost"), **_BAR_STYLE),
    )
    if horizon:
        _update_xaxis_horizon(fig, horizon)
    return fig


def get_duration_figure(
    subject: Union[
        Union[Component, System, Project, Compound],
        Sequence[Union[Component, System, Project, Compound]],
    ],
    horizon: Optional[Horizon] = None,
    bar_width: str = "unit",
) -> go.Figure:
    """Get a duration bar chart figure.

    Arguments:
        subject: Planning object(s) with maintenance tasks with duration attached.
        horizon: Optional horizon to apply. It's start is used as the X-axis offset to
            apply and the end is used to then set the upper bound of the X-axis.
        bar_width: How to determine widths of bars shown. 'auto' for Plotly defaults or
            'unit' for widths of 1.

    Returns:
        Duration bar chart figure.
    """
    x_offset = 0 if horizon is None else horizon.start
    fig = go.Figure(
        _get_barchart(subject, x_offset=x_offset, prop="duration", bar_width=bar_width),
        layout=dict(xaxis=dict(title="Time"), yaxis=dict(title="Duration"), **_BAR_STYLE),
    )
    if horizon:
        _update_xaxis_horizon(fig, horizon)
    return fig


def _get_cfp_trace(
    subject: Union[Component, System, Project, Compound],
    xs: list[Union[int, float]],
    x_offset: Union[int, float] = 0.0,
) -> go.Scatter:
    """Get a line trace displaying the CFP of the subject.

    Arguments:
        subject: Planning object with a CFP method.
        xs: Time values to calculate CFP values at.
        x_offset: Value to offset x values with for display on axis.

    Returns:
        Plotly scatter trace.
    """
    ys = [subject.cfp(x) for x in xs]
    if x_offset != 0.0:
        # Redefine xs if offset is supplied.
        xs = [x + x_offset for x in xs]

    return go.Scatter(x=xs, y=ys, name=subject.name, mode="lines")


def _get_barchart(
    subject: Union[
        Union[Component, System, Project, Compound],
        Sequence[Union[Component, System, Project, Compound]],
    ],
    prop: str = "cost",
    x_offset: Union[int, float] = 0.0,
    bar_width: str = "unit",
) -> list[go.Bar]:
    subjects = subject if isinstance(subject, list) else [subject]
    bars = []
    for s in subjects:
        data: dict = dict(names=[], times=[], values=[])
        for m in s.get_ordered_maintenance():
            data["names"].append(m.name)
            data["times"].append(float(m.time + x_offset))
            data["values"].append(getattr(m.task, prop, 0.0))
        width: Optional[list[int]] = len(data["times"]) * [1] if bar_width == "unit" else None
        bars.append(
            go.Bar(
                x=data["times"],
                y=data["values"],
                hovertext=data["names"],
                name=s.name,
                width=width,
            ),
        )
    return bars


def _update_xaxis_horizon(fig: go.Figure, horizon: Horizon):
    lower = getattr(horizon, "start")
    upper = getattr(horizon, "end")
    xaxis = dict(range=(lower, upper))
    fig.update_layout(xaxis=xaxis)


def get_procedures_plot(procedures: list[Procedure]):
    """Get a procedures plot where systems are to be plotted versus standardized
    procedures (groups of tasks) and their duration and cost.

    Arguments:
        procedures: A list of procedures to be executed.
    """
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.2, 0.2],
    )

    kinds = sorted(set(p.kind for p in procedures))
    kind_to_index = {value: i for i, value in enumerate(kinds)}
    _times = sorted(set(p.time for p in procedures))
    systems = sorted(set(p.system for p in procedures))
    system_to_index = {value: i for i, value in enumerate(systems)}

    procedures = sorted(procedures, key=lambda p: (p.kind, p.system, p.time, -p.cost, -p.duration))

    colors = {kind: COLORS[i % len(COLORS)] for i, kind in enumerate(kinds)}
    hm_colors = [(float(i), colors[kind]) for i, kind in enumerate(kinds)]

    xs = list(range(int(_times[0]), int(_times[-1] + 1)))

    heatmap_z: list[list[Optional[int]]] = [[None for j in xs] for i in systems]
    heatmap_text: list[list[Optional[str]]] = [[None for j in xs] for i in systems]
    for p in procedures:
        row, col = system_to_index[p.system], int(p.time) - xs[0]
        heatmap_z[row][col] = kind_to_index[p.kind]
        heatmap_text[row][col] = p.kind

    for kind_index, kind in enumerate(kinds):
        times: list[Union[int, float]] = []
        costs: list[Union[int, float]] = []
        duras: list[Union[int, float]] = []
        objs: list[int] = []

        for p in procedures:
            if p.kind != kind:
                continue
            times.append(p.time)
            costs.append(p.cost)
            duras.append(p.duration)
            objs.append(system_to_index[p.system])

        # Heatmap, with adjusted colormaps to trick plotly's via legend toggles.
        hm_colors = [colors[kind] if kind == _kind else "rgba(0,0,0,0)" for _kind in kinds]

        fig.add_trace(
            go.Heatmap(
                x=xs,
                y=systems,
                z=heatmap_z,
                legendgroup=kind,
                name="procedures",
                colorscale=hm_colors,
                showlegend=False,
                showscale=False,
                hoverongaps=False,
                xgap=2,
                ygap=2,
                hovertemplate="time: %{x}<br>system: %{y}<br>" + "procedure: %{customdata}",
                customdata=heatmap_text,
            )
        )

        # Cost
        fig.add_trace(
            go.Bar(
                x=times,
                y=costs,
                legendgroup=kind,
                name=kind,
                marker_color=colors[kind],
                hovertemplate="time: %{x}<br>cost: %{y}<br>object: %{customdata}",
                customdata=[systems[obj] for obj in objs],
            ),
            2,
            1,
        )

        # Duration
        fig.add_trace(
            go.Bar(
                x=times,
                y=duras,
                legendgroup=kind,
                name=kind,
                showlegend=False,
                marker_color=colors[kind],
            ),
            3,
            1,
        )

    fig.layout.update(
        xaxis=dict(showticklabels=True),
        xaxis2=dict(showticklabels=True),
        xaxis3=dict(title="Time"),
        yaxis1=dict(title="Subject"),
        yaxis2=dict(title="Cost"),
        yaxis3=dict(title="Duration"),
        barmode="stack",
        bargap=0.0,
        bargroupgap=0.1,
    )
    return fig
