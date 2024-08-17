import pandas as pd
import plotly.io as pio
from fasthtml import Div
from fh_plotly import plotly2fasthtml
from plotly import express as px, graph_objects as go

from ui.state import ui_state

pio.templates.default = "plotly_dark"


def SpeedCharts():
    # TODO: reduce resolution of charts at a certain threshold or similar
    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        speed=[car.current_speed for car in ui_state.simulation.car_history.values()],
    ))
    speed_histogram = px.line(data_frame, x="time", y="speed", title='Speed of the car')

    # Total distance driven
    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        distance=[car.distance_driven for car in ui_state.simulation.car_history.values()],
    ))
    distance_histogram = px.line(data_frame, x="time", y="distance", title='Distance Driven')

    # Total lap counter
    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        lap=[car.lap_counter for car in ui_state.simulation.car_history.values()],
    ))
    lap_histogram = px.line(data_frame, x="time", y="lap", title='Lap Counter')

    return Div(
        plotly2fasthtml(speed_histogram),
        plotly2fasthtml(distance_histogram),
        plotly2fasthtml(lap_histogram),
        hx_swap_oob="true",
        cls="chart-row",
        id="chart-row")


def EnergyCharts():
    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        energy=[car.energy_stored for car in ui_state.simulation.car_history.values()],
    ))
    energy_histogram = px.line(data_frame, x="time", y="energy", title='Energy Stored')

    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        energy=[car.energy_used for car in ui_state.simulation.car_history.values()],
    ))
    energy_usage_histogram = px.line(data_frame, x="time", y="energy", title='Energy Used')

    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        energy=[car.energy_used_per_distance for car in ui_state.simulation.car_history.values()],
    ))
    energy_usage_per_distance_histogram = px.line(data_frame, x="time", y="energy",
                                                  title='Energy Used per Distance')

    return Div(
        plotly2fasthtml(energy_histogram),
        plotly2fasthtml(energy_usage_histogram),
        plotly2fasthtml(energy_usage_per_distance_histogram),
        hx_swap_oob="true",
        cls="chart-row2",
        id="chart-row2"
    )


def DeltaCharts():
    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        acceleration=[car.delta_input.acceleration for car in ui_state.simulation.car_history.values()],
    ))
    acceleration_histogram = px.line(data_frame, x="time", y="acceleration", title='Acceleration')

    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        distance_delta=[car.delta_input.distance_delta for car in ui_state.simulation.car_history.values()],
    ))
    distance_delta_histogram = px.line(data_frame, x="time", y="distance_delta", title='Distance Delta')

    data_frame = pd.DataFrame(dict(
        time=ui_state.simulation.car_history.keys(),
        energy_delta=[car.delta_input.energy_delta for car in ui_state.simulation.car_history.values()],
    ))
    energy_delta_histogram = px.line(data_frame, x="time", y="energy_delta", title='Energy Delta')

    return Div(
        plotly2fasthtml(acceleration_histogram),
        plotly2fasthtml(distance_delta_histogram),
        plotly2fasthtml(energy_delta_histogram),
        hx_swap_oob="true",
        cls="chart-row3",
        id="chart-row3"
    )


def SideCharts():
    # TODO: add delta for speed based on tick delta
    speed_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ui_state.simulation.car.current_speed,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Speed (m/s)"},
        gauge={'axis': {'range': [None, ui_state.simulation.car.max_speed]}, }
    ))

    energy_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ui_state.simulation.car.energy_stored,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Energy Stored (Wh)"},
        gauge={'axis': {'range': [None, 10_000]}, }
    ))

    return Div(
        Div(f"Active: {"✅" if ui_state.simulation_running else "❌"}"),
        plotly2fasthtml(speed_gauge),
        plotly2fasthtml(energy_gauge),
        hx_swap_oob="true",
        cls="chart-side",
        id="chart-side")
