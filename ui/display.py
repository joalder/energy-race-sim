import asyncio
import logging
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from fasthtml.common import *
from fh_plotly import plotly2fasthtml, plotly_headers

from simulation.car import Car
from simulation.environment import Environment
from simulation.position import Position
from simulation.simulation import Simulation
from simulation.tile import Direction
from simulation.track import TrackBuilder
from ui.render import TrackRendererCanvas, VehicleRendererCanvas

log = logging.getLogger(__name__)

pico_amber = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.pumpkin.min.css")
custom_css = Link(rel="stylesheet", type="text/css", href="static/style.css")
htmx_ws = Script(src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js")
app = FastHTML(hdrs=(pico_amber, custom_css, htmx_ws, plotly_headers), debug=True)
route = app.route

# Serve static files
app.mount("/static", StaticFiles(directory="ui/static"), name="static")
setup_toasts(app)

pio.templates.default = "plotly_dark"


def create_simulation():
    car = Car(max_acceleration=2, max_speed=33, energy_stored=10_000, height=1.5, track_width=1.9,
              tire_friction_coefficient=0.8)
    track = TrackBuilder("Basic Oval", Position(50, 50, 0, 0)) \
        .into_straight(500) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(50) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(500) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(50) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .loop()
    environment = Environment(track)
    simulation = Simulation(car, environment)
    simulation.setup()
    return simulation


@dataclass
class UiState:
    simulation_running: bool = False
    simulation: Simulation = create_simulation()
    ticks_per_second: int = 1
    seconds_per_tick: int = 1
    single_step: bool = False


ui_state = UiState()


def TrackView():
    """
    Create a canvas element for the track, replacing this via htmx seems to cause trouble,
    content vanishes after settling 🤷 Only swap the render scripts and reset before drawing.
    """
    # TODO: create 2nd canvas for vehicle overlay to only redraw vehicles on update
    return Div(
        Canvas(id="track-canvas", width=800, height=600),
        TrackRenderScript(),
        VehicleRenderScript(),
        cls="track-view",
        id="track-view")


def TrackRenderScript():
    return Div(
        Script(TrackRendererCanvas(ui_state.simulation.environment.track).generate_js()),
        hx_swap_oob="true",
        id="track-render")


def VehicleRenderScript():
    return Div(
        Script(VehicleRendererCanvas(ui_state.simulation.car).generate_js()),
        hx_swap_oob="true",
        id="vehicle-render")


def ControlBar():
    start_button = Button("Start", hx_put="/run", hx_target='#simulation', hx_swap='none')
    pause_button = Button("Pause", hx_put="/pause", hx_target='#simulation', hx_swap='none')
    reset_button = Button("Reset", hx_put="/reset", hx_target='#simulation', hx_swap='none')
    step_button = Button("Step", hx_put="/step", hx_target='#simulation', hx_swap='none')

    slider_seconds_per_tick = Label(
        f"Simulation Resolution (Second/Tick): {ui_state.seconds_per_tick}",
        Input(type="range", _id='slider_seconds_per_tick', name='seconds_per_tick', min=1, max=60, step=1,
              value=ui_state.seconds_per_tick, hx_trigger="change", hx_put="/update-seconds-per-tick"),
        _for='slider_seconds_per_tick'
    )
    slider_ticks_per_second = Label(
        f"Simulation Speed (Ticks/Second) {ui_state.ticks_per_second}",
        Input(type="range", _id='slider_ticks_per_second', name='ticks_per_second', min=1, max=60, step=1,
              value=ui_state.ticks_per_second, hx_trigger="change", hx_put="/update-ticks-per-second"),
        _for='slider_ticks_per_second'
    )

    return Div(
        start_button, pause_button, reset_button, step_button, slider_seconds_per_tick, slider_ticks_per_second,
        hx_swap_oob="true",
        cls="controls",
        id="control-bar")


def SpeedCharts():
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


def SimulationUi():
    return Div(
        Div(
            P(f"Track: {ui_state.simulation.environment.track.name}"),
            cls="header",
            id="header"
        ),
        ControlBar(),
        TrackView(),
        SideCharts(),
        SpeedCharts(),
        EnergyCharts(),
        DeltaCharts(),
        cls="container-grid",
        id="simulation")


def Home():
    main = Main(SimulationUi(), hx_ext="ws", ws_connect="/socket")
    footer = Footer(P("The footer..."))
    return Title("Energy Race Sim"), main, footer


@route('/')
def get():
    return Home()


sessions: list = []


async def update_sessions(elements: list = None):
    if elements is None:
        elements = [TrackRenderScript(),
                    VehicleRenderScript(),
                    SideCharts(),
                    SpeedCharts(),
                    EnergyCharts(),
                    DeltaCharts()]

    for i, session in enumerate(sessions):
        try:
            # Somehow cannot send all of them together, so make a message out of each
            # TODO: can we await all of them together?
            for element in elements:
                await session(element)
        except:
            log.exception(f"Failure on updating simulation for session {i}")
            sessions.pop(i)


async def on_connect(send):
    sessions.append(send)


async def on_disconnect(send):
    await update_sessions()


@app.ws('/socket', conn=on_connect, disconn=on_disconnect)
async def web_socket(msg: str, send):
    pass


async def background_task():
    while True:
        time_per_tick = 1 / ui_state.ticks_per_second
        update_interval = 1
        update_needed = False

        start_time = datetime.now()

        for _ in range(ui_state.ticks_per_second):
            if ui_state.simulation_running and not ui_state.simulation.is_done() and len(sessions) > 0:
                update_needed = True
                ui_state.simulation.tick(ui_state.seconds_per_tick)

                # TODO: this does not seem to work: Update track and vehicle to get real smooth animation
                await update_sessions([TrackRenderScript(), VehicleRenderScript()])

                if ui_state.single_step:
                    ui_state.simulation_running = False
                    ui_state.single_step = False

        if update_needed:
            await update_sessions()

        time_used = datetime.now() - start_time

        if time_used.total_seconds() < update_interval:
            # refresh interval static 1 second for now
            if time_used.total_seconds() > 0.001:
                log.debug(f"Background task took {time_used.total_seconds():.3f}s")
            await asyncio.sleep(update_interval - time_used.total_seconds())
        else:
            log.warning(f"Lagging in simulation. Background task took {time_used.total_seconds()}s")

        # TODO: compensate lag and other overhead over time based on real time measurements
        # TODO: find reason why simulation stops after a 600s 🤔


background_task_coroutine = asyncio.create_task(background_task())


@route('/run')
async def put(session):
    ui_state.simulation_running = True
    add_toast(session, "Simulation started")
    await update_sessions()


@route('/step')
async def put(session):
    ui_state.simulation_running = True
    ui_state.single_step = True
    add_toast(session, "Simulating 1 step")
    await update_sessions()


@route('/pause')
async def put(session):
    ui_state.simulation_running = False
    add_toast(session, "Simulation paused")
    await update_sessions()


@route("/reset")
async def put(session):
    ui_state.simulation_running = False
    ui_state.simulation = create_simulation()
    add_toast(session, "Simulation reset")
    await update_sessions()


@route("/update-seconds-per-tick")
async def put(seconds_per_tick: int):
    global ui_state
    ui_state.seconds_per_tick = seconds_per_tick
    return ControlBar()


@route("/update-ticks-per-second")
async def put(ticks_per_second: int):
    global ui_state
    ui_state.ticks_per_second = ticks_per_second
    return ControlBar()
