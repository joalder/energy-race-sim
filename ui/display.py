import asyncio
import logging
from datetime import datetime

from fasthtml.common import *

from simulation.car import Car
from simulation.environment import Environment
from simulation.position import Position
from simulation.simulation import Simulation
from simulation.tile import Direction, StraightTile, CornerTile
from simulation.track import TrackBuilder

log = logging.getLogger(__name__)

htmx_ws = Script(src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js")
app = FastHTMLWithLiveReload(hdrs=(picolink, htmx_ws))
route = app.route

setup_toasts(app)


def create_simulation():
    car = Car(max_acceleration=2, max_speed=33, energy_stored=10_000)
    track = TrackBuilder("Basic Oval", Position(50, 50, 0, 0)) \
        .into_straight(25) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(12) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(25) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(12) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .loop()
    environment = Environment(track)
    simulation = Simulation(car, environment)
    simulation.setup()
    return simulation


class UiState:
    def __init__(self):
        self.simulation_running = False
        self.simulation = create_simulation()
        self.ticks_per_second = 1
        self.seconds_per_tick = 1


ui_state = UiState()


class TrackRendererCanvas:
    def __init__(self, track):
        self.track = track

    def generate_js(self, canvas_id="track-canvas"):
        script = f"""
        var canvas = document.getElementById('{canvas_id}');
        var context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.lineWidth = 2;
        context.strokeStyle = 'white';
        """

        for tile in self.track.tiles:
            # TODO: make a pretty match statement or similar
            if isinstance(tile, StraightTile):
                script += self._generate_straight_line(tile)
            elif isinstance(tile, CornerTile):
                script += self._generate_corner(tile)

        log.info(f"Track for reference: {self.track}")
        return script

    def _generate_straight_line(self, tile: StraightTile):
        points = tile.get_defining_points()
        return f"""
            context.fillStyle = 'blue';
            context.beginPath();
            context.arc({tile.origin.x}, {tile.origin.y}, 2, 0, 2 * Math.PI);
            context.fill();
            context.fillStyle = 'grey';
            context.beginPath();
            context.moveTo({points[0].x}, {points[0].y});
            context.lineTo({points[1].x}, {points[1].y});
            context.lineTo({points[3].x}, {points[3].y});
            context.lineTo({points[2].x}, {points[2].y});
            context.fill();
            """

    def _generate_corner(self, tile: CornerTile):
        radius_center = tile.get_radius_center()
        # TODO: share logic with tile.py
        radius = tile.width + tile.inner_radius if tile.direction == Direction.RIGHT else tile.inner_radius
        clockwise = 'true' if tile.direction == Direction.LEFT else 'false'
        rad_offset = math.pi / 2 if tile.direction == Direction.LEFT else -math.pi / 2
        return f"""
            context.fillStyle = 'red';
            context.beginPath();
            context.arc({tile.origin.x}, {tile.origin.y}, 2, 0, 2 * Math.PI);
            context.fill();
            context.fillStyle = 'green';
            context.beginPath();
            context.arc({radius_center.x}, {radius_center.y}, 2, 0, 2 * Math.PI);
            context.fill();
            context.beginPath();
            context.arc({radius_center.x}, {radius_center.y}, {radius}, {tile.origin.orientation_rad + rad_offset}, {tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {clockwise});
            context.stroke();
            """


def TrackView():
    return Div(
        Canvas(id="track-canvas", width=800, height=400),
        Script(TrackRendererCanvas(ui_state.simulation.environment.track).generate_js()),
        id="track-view")


def SimulationUi():
    return Div(
        P(f"Running? {ui_state.simulation_running}"),
        P(f"Car: {ui_state.simulation.car.status_static()}"),
        TrackView(),
        ControlBar(),
        id="simulation")


def ControlBar():
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
    start_button = Button("Start", hx_put="/run", hx_target='#simulation', hx_swap='none')
    pause_button = Button("Pause", hx_put="/pause", hx_target='#simulation', hx_swap='none')
    reset_button = Button("Reset", hx_put="/reset", hx_target='#simulation', hx_swap='none')

    return Div(
        Div(
            start_button, pause_button, reset_button
        ),
        Div(
            slider_seconds_per_tick, slider_ticks_per_second
        ))


def Home():
    main = Main(SimulationUi(), hx_ext="ws", ws_connect="/socket")
    footer = Footer(P("The footer..."))
    return Title("Energy Race Sim"), main, footer


@route('/')
def get(): return Home()


player_queue = []


async def update_players():
    for i, player in enumerate(player_queue):
        try:
            await player(SimulationUi())
        except:
            log.exception(f"Failure on updating simulation for player {i}")
            player_queue.pop(i)


async def on_connect(send): player_queue.append(send)


async def on_disconnect(send): await update_players()


@app.ws('/socket', conn=on_connect, disconn=on_disconnect)
async def web_socket(msg: str, send): pass


async def background_task():
    while True:
        start_time = datetime.now()

        for _ in range(ui_state.ticks_per_second):
            if ui_state.simulation_running and not ui_state.simulation.is_done() and len(player_queue) > 0:
                ui_state.simulation.tick(ui_state.seconds_per_tick)
                await update_players()

        time_used = datetime.now() - start_time

        if time_used.total_seconds() < 1:
            # refresh interval static 1 second for now
            await asyncio.sleep(1 - time_used.total_seconds())
        else:
            log.warning(f"Background task took {time_used.total_seconds()}s")


background_task_coroutine = asyncio.create_task(background_task())


@route('/run')
async def put(session):
    ui_state.simulation_running = True
    add_toast(session, "Simulation started")
    await update_players()


@route('/pause')
async def put(session):
    ui_state.simulation_running = False
    add_toast(session, "Simulation paused")
    await update_players()


@route("/reset")
async def put(session):
    ui_state.simulation_running = False
    ui_state.simulation = create_simulation()
    add_toast(session, "Simulation reset")
    await update_players()


@route("/update-seconds-per-tick")
async def put(seconds_per_tick: int):
    global ui_state
    ui_state.seconds_per_tick = seconds_per_tick
    await update_players()


@route("/update-ticks-per-second")
async def put(ticks_per_second: int):
    global ui_state
    ui_state.ticks_per_second = ticks_per_second
    await update_players()
