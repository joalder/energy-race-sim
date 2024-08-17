import logging
import math

from fasthtml import Div, Canvas, Script

from simulation.car import Car
from simulation.tile import StraightTile, CornerTile, Direction
from simulation.track import Track
from ui.state import ui_state

log = logging.getLogger(__name__)


class TrackRendererCanvas:
    def __init__(self, track: Track):
        self.track = track
        self.track_color = 'grey'
        self.track_limit_color = 'white'
        self.render_debug_points = False
        self.debug_point_size = 2

    def generate_js(self, canvas_id="track-canvas"):
        script = f"""
        console.log('Rendering track');
        var canvas = document.getElementById('{canvas_id}');
        var ctx = canvas.getContext('2d');
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = '{self.track_limit_color}';
        """

        for tile in self.track.tiles:
            # TODO: make a pretty match statement or similar
            if isinstance(tile, StraightTile):
                script += self._generate_straight_line(tile)
            elif isinstance(tile, CornerTile):
                script += self._generate_corner(tile)

        script += """
        console.log('Track rendered');
        """

        return script

    def _generate_straight_line(self, tile: StraightTile):
        points = tile.get_defining_points()
        return f"""
            // Tarmac
            ctx.fillStyle = '{self.track_color}';
            ctx.beginPath();
            ctx.moveTo({points[0].x}, {points[0].y});
            ctx.lineTo({points[1].x}, {points[1].y});
            ctx.lineTo({points[3].x}, {points[3].y});
            ctx.lineTo({points[2].x}, {points[2].y});
            ctx.fill();
            
            // Track limit lines
            //ctx.strokeStyle = '{self.track_limit_color}';
            ctx.beginPath();
            ctx.moveTo({points[0].x}, {points[0].y});
            ctx.lineTo({points[2].x}, {points[2].y});
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo({points[1].x}, {points[1].y});
            ctx.lineTo({points[3].x}, {points[3].y});
            ctx.stroke();
            """ + self._generate_debug_points(points, 'blue', 'orange')

    def _generate_corner(self, tile: CornerTile):
        points = tile.get_defining_points()
        radius_center = tile.get_radius_center()
        # TODO: make this less stupid and noisy
        left_radius = tile.width + tile.inner_radius if tile.direction == Direction.RIGHT else tile.inner_radius
        right_radius = tile.width + tile.inner_radius if tile.direction == Direction.LEFT else tile.inner_radius
        direction_left = 'true' if tile.direction == Direction.LEFT else 'false'
        direction_right = 'true' if tile.direction == Direction.RIGHT else 'false'
        rad_offset = math.pi / 2 if tile.direction == Direction.LEFT else -math.pi / 2
        return f"""
            // Tarmac
            ctx.fillStyle = '{self.track_color}';
            ctx.beginPath();
            ctx.arc({radius_center.x}, {radius_center.y}, {left_radius}, {tile.origin.orientation_rad + rad_offset}, {tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {direction_left});
            ctx.lineTo({points[3].x}, {points[3].y});
            ctx.arc({radius_center.x}, {radius_center.y}, {right_radius},{tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {tile.origin.orientation_rad + rad_offset},  {direction_right});
            ctx.fill();
            
            // Track limit lines
            //ctx.strokeStyle = '{self.track_limit_color}';
            ctx.beginPath();
            ctx.arc({radius_center.x}, {radius_center.y}, {left_radius}, {tile.origin.orientation_rad + rad_offset}, {tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {direction_left});
            ctx.stroke();
            ctx.beginPath();
            ctx.arc({radius_center.x}, {radius_center.y}, {right_radius},{tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {tile.origin.orientation_rad + rad_offset},  {direction_right});
            ctx.stroke();
            """ + self._generate_debug_points(points, 'red', 'green')

    def _generate_debug_points(self, points, start_color: str, end_color: str):
        return f"""
            ctx.fillStyle = '{start_color}';
            ctx.beginPath();
            ctx.arc({points[0].x}, {points[0].y}, {self.debug_point_size}, {points[0].orientation_rad - math.pi / 2}, {points[0].orientation_rad + math.pi / 2});
            ctx.fill();
            ctx.beginPath();
            ctx.arc({points[1].x}, {points[1].y}, {self.debug_point_size}, {points[1].orientation_rad - math.pi / 2}, {points[1].orientation_rad + math.pi / 2});
            ctx.fill();
            ctx.fillStyle = '{end_color}';
            ctx.beginPath();
            ctx.arc({points[2].x}, {points[2].y}, {self.debug_point_size}, {points[2].orientation_rad + math.pi / 2}, {points[2].orientation_rad - math.pi / 2});
            ctx.fill();
            ctx.beginPath();
            ctx.arc({points[3].x}, {points[3].y}, {self.debug_point_size}, {points[3].orientation_rad + math.pi / 2}, {points[3].orientation_rad - math.pi / 2});
            ctx.fill();
            """ if self.render_debug_points else ""


class VehicleRendererCanvas:
    def __init__(self, car: Car):
        self.color = "red"
        self.car = car

    def generate_js(self, canvas_id="track-canvas"):
        location = self.car.location.get_absolute_position()

        script = f"""
            var canvas = document.getElementById('{canvas_id}');
            var ctx = canvas.getContext('2d');
            
            ctx.fillStyle = '{self.color}';
            ctx.beginPath();
            ctx.arc({location.x}, {location.y}, 3, 0, 2 * Math.PI);
            ctx.fill();
            """

        script += """
            console.log('Vehicle rendered');
            """

        return script


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
