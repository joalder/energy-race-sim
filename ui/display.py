import asyncio
import logging
from datetime import datetime

from fasthtml.common import *
from fh_plotly import plotly_headers

import ui.state
from ui.chart import SpeedCharts, EnergyCharts, DeltaCharts, SideCharts
from ui.render import TrackView, TrackRenderScript, VehicleRenderScript
from ui.state import create_simulation, ui_state

log = logging.getLogger(__name__)

pico_amber = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.pumpkin.min.css")
custom_css = Link(rel="stylesheet", type="text/css", href="static/style.css")
htmx_ws = Script(src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js")
app = FastHTML(hdrs=(pico_amber, custom_css, htmx_ws, plotly_headers), debug=True)
route = app.route

# Serve static files
app.mount("/static", StaticFiles(directory="ui/static"), name="static")
setup_toasts(app)


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
    footer = Footer(A("GitHub", href="https://github.com/joalder/energy-race-sim"))
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
    ui.state.ui_state.seconds_per_tick = seconds_per_tick
    return ControlBar()


@route("/update-ticks-per-second")
async def put(ticks_per_second: int):
    ui.state.ui_state.ticks_per_second = ticks_per_second
    return ControlBar()
