import logging
import math
from dataclasses import dataclass

from fasthtml import Div, Canvas, Script

from simulation.vehicle import Vehicle
from simulation.tile import StraightTile, CornerTile, Direction
from simulation.track import Track
from ui.state import ui_state

log = logging.getLogger(__name__)


@dataclass
class TrackRendererCanvas:
    track: Track
    track_color: str = 'grey'
    track_limit_color: str = 'white'
    render_scale: float = 1
    render_rotation_rad: float = 0
    render_debug_points: bool = False
    debug_point_size: int = 2

    def generate_js(self, canvas_id="track-canvas"):
        script = f"""
        console.log('Rendering track');
        var canvas = document.getElementById('{canvas_id}');
        var ctx = canvas.getContext('2d');
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = '{self.track_limit_color}';
        """

        # TODO: render start/finish line
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
            // -- Straight {tile.length}m --
            // Tarmac
            ctx.fillStyle = '{self.track_color}';
            ctx.beginPath();
            ctx.moveTo({points[0].x * self.render_scale}, {points[0].y * self.render_scale});
            ctx.lineTo({points[1].x * self.render_scale}, {points[1].y * self.render_scale});
            ctx.lineTo({points[3].x * self.render_scale}, {points[3].y * self.render_scale});
            ctx.lineTo({points[2].x * self.render_scale}, {points[2].y * self.render_scale});
            ctx.fill();
            
            // Track limit lines
            //ctx.strokeStyle = '{self.track_limit_color}';
            ctx.beginPath();
            ctx.moveTo({points[0].x * self.render_scale}, {points[0].y * self.render_scale});
            ctx.lineTo({points[2].x * self.render_scale}, {points[2].y * self.render_scale});
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo({points[1].x * self.render_scale}, {points[1].y * self.render_scale});
            ctx.lineTo({points[3].x * self.render_scale}, {points[3].y * self.render_scale});
            ctx.stroke();
            """ + self._generate_debug_points(points, 'blue', 'orange')

    def _generate_corner(self, tile: CornerTile):
        points = tile.get_defining_points()
        radius_center = tile.get_radius_center()
        # TODO: make this less stupid and noisy, left corner is now drawn in reverse??
        left_radius = tile.width + tile.inner_radius if tile.direction == Direction.RIGHT else tile.inner_radius
        right_radius = tile.width + tile.inner_radius if tile.direction == Direction.LEFT else tile.inner_radius
        direction_left_arc, direction_right_arc = 'false', 'true'
        rad_offset = math.pi / 2 if tile.direction == Direction.LEFT else -math.pi / 2
        arc_start_rad = tile.origin.orientation_rad + rad_offset + (
            -tile.alpha_rad if tile.direction == Direction.LEFT else 0)
        arc_end_rad = tile.origin.orientation_rad + rad_offset + (
            tile.alpha_rad if tile.direction == Direction.RIGHT else 0)
        point_for_line = points[3] if tile.direction == Direction.RIGHT else points[0]
        return f"""
            // -- Corner {tile.direction.name} {tile.alpha}° {tile.inner_radius}m --
            // Tarmac
            ctx.fillStyle = '{self.track_color}';
            ctx.beginPath();
            ctx.arc({radius_center.x * self.render_scale}, {radius_center.y * self.render_scale}, {left_radius * self.render_scale}, {arc_start_rad}, {arc_end_rad}, {direction_left_arc});
            ctx.lineTo({point_for_line.x * self.render_scale}, {point_for_line.y * self.render_scale});
            ctx.arc({radius_center.x * self.render_scale}, {radius_center.y * self.render_scale}, {right_radius * self.render_scale}, {arc_end_rad}, {arc_start_rad}, {direction_right_arc});
            ctx.fill();
            
            // Track limit lines
            //ctx.strokeStyle = '{self.track_limit_color}';
            ctx.beginPath();
            ctx.arc({radius_center.x * self.render_scale}, {radius_center.y * self.render_scale}, {left_radius * self.render_scale}, {arc_start_rad}, {arc_end_rad}, {direction_left_arc});
            ctx.stroke();
            ctx.beginPath();
            ctx.arc({radius_center.x * self.render_scale}, {radius_center.y * self.render_scale}, {right_radius * self.render_scale}, {arc_end_rad}, {arc_start_rad}, {direction_right_arc});
            ctx.stroke();
            """ + self._generate_debug_points(points, 'red', 'green')

    def _generate_debug_points(self, points, start_color: str, end_color: str):
        return f"""
            ctx.fillStyle = '{start_color}';
            ctx.beginPath();
            ctx.arc({points[0].x * self.render_scale}, {points[0].y * self.render_scale}, {self.debug_point_size * self.render_scale}, {points[0].orientation_rad - math.pi / 2}, {points[0].orientation_rad + math.pi / 2});
            ctx.fill();
            ctx.beginPath();
            ctx.arc({points[1].x * self.render_scale}, {points[1].y * self.render_scale}, {self.debug_point_size * self.render_scale}, {points[1].orientation_rad - math.pi / 2}, {points[1].orientation_rad + math.pi / 2});
            ctx.fill();
            ctx.fillStyle = '{end_color}';
            ctx.beginPath();
            ctx.arc({points[2].x * self.render_scale}, {points[2].y * self.render_scale}, {self.debug_point_size * self.render_scale}, {points[2].orientation_rad + math.pi / 2}, {points[2].orientation_rad - math.pi / 2});
            ctx.fill();
            ctx.beginPath();
            ctx.arc({points[3].x * self.render_scale}, {points[3].y * self.render_scale}, {self.debug_point_size * self.render_scale}, {points[3].orientation_rad + math.pi / 2}, {points[3].orientation_rad - math.pi / 2});
            ctx.fill();
            """ if self.render_debug_points else ""


@dataclass
class VehicleRendererCanvas:
    vehicle: Vehicle
    color: str = "red"
    render_scale: float = 1

    def generate_js(self, canvas_id="track-canvas"):
        location = self.vehicle.location.get_absolute_position()

        script = f"""
            var canvas = document.getElementById('{canvas_id}');
            var ctx = canvas.getContext('2d');
            
            ctx.fillStyle = '{self.color}';
            ctx.beginPath();
            ctx.arc({location.x * self.render_scale}, {location.y * self.render_scale}, 3, 0, 2 * Math.PI);
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
        Canvas(id="track-canvas", width="600", height="600"),
        TrackRenderScript(),
        VehicleRenderScript(),
        cls="track-view",
        id="track-view")


def TrackRenderScript():
    # TODO: make render scale based on track size/layout
    return Div(
        Script(TrackRendererCanvas(ui_state.simulation.environment.track,
                                   render_scale=ui_state.render_scale).generate_js()),
        hx_swap_oob="true",
        id="track-render")


def VehicleRenderScript():
    return Div(
        Script(VehicleRendererCanvas(ui_state.simulation.vehicle, render_scale=ui_state.render_scale).generate_js()),
        hx_swap_oob="true",
        id="vehicle-render")
