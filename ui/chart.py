import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from fasthtml import Div
from fh_plotly import plotly2fasthtml

from ui.state import ui_state

pio.templates.default = "plotly_dark"


def SpeedCharts():
    # TODO: reduce resolution of charts at a certain threshold or similar
    speed_histogram = vehicle_line_chart_over_time(lambda v: v.current_speed, "Speed (m/s)")
    distance_histogram = vehicle_line_chart_over_time(lambda v: v.distance_driven, "Distance (m)")
    lap_histogram = vehicle_line_chart_over_time(lambda v: v.lap_counter, "Laps")

    return Div(
        plotly2fasthtml(speed_histogram),
        plotly2fasthtml(distance_histogram),
        plotly2fasthtml(lap_histogram),
        hx_swap_oob="true",
        cls="chart-row",
        id="chart-row")


def EnergyCharts():
    energy_histogram = vehicle_line_chart_over_time(lambda v: v.energy_stored, "⚡ Stored (Wh)")
    energy_usage_histogram = vehicle_line_chart_over_time(lambda v: v.energy_used, "⚡ Used (Wh)")
    energy_usage_per_distance_histogram = vehicle_line_chart_over_time(lambda v: v.energy_used_per_distance,
                                                                       "⚡ per Distance (Wh/m)")

    return Div(
        plotly2fasthtml(energy_histogram),
        plotly2fasthtml(energy_usage_histogram),
        plotly2fasthtml(energy_usage_per_distance_histogram),
        hx_swap_oob="true",
        cls="chart-row2",
        id="chart-row2"
    )


def DeltaCharts():
    acceleration_histogram = vehicle_line_chart_over_time(lambda v: v.delta_input.acceleration, "Accel. Δ (m/s²)")
    distance_delta_histogram = vehicle_line_chart_over_time(lambda v: v.delta_input.distance_delta,
                                                            "Distance Δ (m)")
    energy_delta_histogram = vehicle_line_chart_over_time(lambda v: v.delta_input.energy_delta, "Energy Δ (Wh)")

    return Div(
        plotly2fasthtml(acceleration_histogram),
        plotly2fasthtml(distance_delta_histogram),
        plotly2fasthtml(energy_delta_histogram),
        hx_swap_oob="true",
        cls="chart-row3",
        id="chart-row3"
    )


def vehicle_line_chart_over_time(extractor: callable, label_y: str, label_x: str = ''):
    histogram = go.Figure()

    for index, vehicle in enumerate(ui_state.simulation.vehicles):
        data_frame = pd.DataFrame(dict(
            time=ui_state.simulation.vehicle_history.keys(),
            y=[extractor(time_slot[index]) for time_slot in ui_state.simulation.vehicle_history.values()],
        ))
        data_frame['time'] = pd.to_datetime(data_frame['time'], unit='s')
        histogram.add_trace(go.Scatter(x=data_frame['time'], y=data_frame['y'],
                                       mode='lines', name=vehicle.name,
                                       line=dict(color=vehicle.color, ),
                                       ))

    histogram.update_layout(margin=dict(b=20, l=80, r=20, t=20), yaxis_title=label_y, xaxis_title=label_x)
    histogram.update_xaxes(tickformat="%H:%M", dtick=60 * 1000)  # dtick is in milliseconds
    return histogram


def SideCharts():
    # TODO: add delta for speed based on tick delta
    # TODO: make this multi-vehicle compatible
    speed_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ui_state.simulation.vehicles[0].current_speed,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Speed (m/s)"},
        gauge={'axis': {'range': [None, ui_state.simulation.vehicles[0].max_speed]}, }
    ))
    speed_gauge.update_layout(margin=dict(b=20, l=20, r=20, t=70))

    energy_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ui_state.simulation.vehicles[0].energy_stored,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Energy Stored (Wh)"},
        gauge={'axis': {'range': [None, 10_000]}, }
    ))
    energy_gauge.update_layout(margin=dict(b=20, l=20, r=20, t=70))

    return Div(
        Div(f"Active: {"✅" if ui_state.simulation_running else "❌"}"),
        plotly2fasthtml(speed_gauge),
        plotly2fasthtml(energy_gauge),
        hx_swap_oob="true",
        cls="chart-side",
        id="chart-side")
