import logging
import math

from simulation.tile import StraightTile, CornerTile, Direction

log = logging.getLogger(__name__)


class TrackRendererCanvas:
    def __init__(self, track):
        self.track = track
        self.track_color = 'grey'
        self.render_debug_points = True
        self.debug_point_size = 2

    def generate_js(self, canvas_id="track-canvas"):
        script = f"""
        var canvas = document.getElementById('{canvas_id}');
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'white';
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
            ctx.fillStyle = '{self.track_color}';
            ctx.beginPath();
            ctx.moveTo({points[0].x}, {points[0].y});
            ctx.lineTo({points[1].x}, {points[1].y});
            ctx.lineTo({points[3].x}, {points[3].y});
            ctx.lineTo({points[2].x}, {points[2].y});
            ctx.fill();
            """ + self._generate_debug_poitns(points, 'blue', 'orange') if self.render_debug_points else ""

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
            ctx.fillStyle = '{self.track_color}';
            ctx.beginPath();
            ctx.arc({radius_center.x}, {radius_center.y}, {left_radius}, {tile.origin.orientation_rad + rad_offset}, {tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {direction_left});
            ctx.lineTo({points[3].x}, {points[3].y});
            ctx.arc({radius_center.x}, {radius_center.y}, {right_radius},{tile.origin.orientation_rad + tile.alpha_rad + rad_offset}, {tile.origin.orientation_rad + rad_offset},  {direction_right});
            ctx.fill();
            """ + self._generate_debug_poitns(points, 'red', 'green') if self.render_debug_points else ""

    def _generate_debug_poitns(self, points, start_color: str, end_color: str):
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
            """