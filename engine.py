#  Copyright (c) 2019 Pavel Vavruska
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import sys
import math
import logging
import traceback
import pygame
import pygame.locals as pylocs

from mathematics.graph.nodes import Dijkstra
from constants import Constants
from renderer import Renderer
from mathematics.raycasting.raycaster import Raycaster

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Engine:

    def __init__(self, player, game_map, config):
        # constructor injection
        self.player = player
        self.game_map = game_map
        self.config = config

        # canvas positioning
        self.mini_map_offset_x = Constants.WINDOW_WIDTH - game_map.size_x * Constants.MULTIPLICATOR_MINIMAP
        self.mini_map_offset_y = 0

        # pygame init
        pygame.init()
        self.font = pygame.font.Font(None, 30)
        self.surface = pygame.Surface((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        pygame.display.set_caption('Pygame - pixel by pixel raycaster')
        self.screen = pygame.display.set_mode((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()  # initialise clock
        pygame.key.set_repeat(True)  # enable key holding

        # variables
        self.path = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pylocs.QUIT:
                return True
            elif event.type == pylocs.MOUSEBUTTONDOWN:
                mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
                cor_in_map_x = int((mouse_pos_x - self.mini_map_offset_x) / Constants.MULTIPLICATOR_MINIMAP)
                cor_in_map_y = int(mouse_pos_y / Constants.MULTIPLICATOR_MINIMAP)
                if (
                        self.game_map.get_at(cor_in_map_x, cor_in_map_y) == -1 and
                        mouse_pos_x > self.mini_map_offset_x
                ):
                    if self.path:
                        self.path.clear()
                    dijkstra = Dijkstra(
                        self.game_map.data,
                        (int(self.player.x), int(self.player.y)),
                        (cor_in_map_x, cor_in_map_y)
                    )
                    try:
                        dijkstra.start()
                        self.path = dijkstra.get_shortest_path()
                    except ValueError:
                        _logger.error('Road must be selected, not wall.')
                    except KeyError:
                        traceback.print_exc(file=sys.stdout)
                    except IndexError:
                        traceback.print_exc(file=sys.stdout)

            elif event.type == pylocs.KEYDOWN:
                if event.key == pylocs.K_w:
                    self.player.set_velocity_x(self.player.velocity_x + math.cos(math.radians(self.player.angle)) / 5)
                    self.player.set_velocity_y(self.player.velocity_y + math.sin(math.radians(self.player.angle)) / 5)

                if event.key == pylocs.K_s:
                    self.player.set_velocity_x(self.player.velocity_x - math.cos(math.radians(self.player.angle)) / 5)
                    self.player.set_velocity_y(self.player.velocity_y - math.sin(math.radians(self.player.angle)) / 5)

                if event.key == pylocs.K_d:
                    self.player.set_velocity_angle(self.player.velocity_angle + 5)

                if event.key == pylocs.K_a:
                    self.player.set_velocity_angle(self.player.velocity_angle - 5)

                if event.key == pylocs.K_p:
                    self.config.toggle_perspective_correction_on()

                if event.key == pylocs.K_l:
                    self.config.toggle_dynamic_lighting()

                if event.key == pylocs.K_t:
                    self.config.toggle_texture_filtering()

                if event.key == pylocs.K_UP:
                    self.config.increase_pixel_size()

                if event.key == pylocs.K_DOWN:
                    self.config.decrease_pixel_size()
        return False

    def handle_path(self):
        _, wanted_y, wanted_x = self.path[-1]
        cur_x = self.player.x
        cur_y = self.player.y
        cur_angle = self.player.angle

        wanted_x += Constants.MAP_HALF_COORDINATE
        wanted_y += Constants.MAP_HALF_COORDINATE

        d_x = wanted_x - cur_x
        d_y = wanted_y - cur_y
        d_r = math.atan2(d_y, d_x)

        if cur_x - Constants.MIN_DELTA_POSITION > wanted_x:
            self.player.set_x(self.player.x - Constants.MIN_DELTA_POSITION)
        elif cur_x + Constants.MIN_DELTA_POSITION < wanted_x:
            self.player.set_x(self.player.x + Constants.MIN_DELTA_POSITION)

        if cur_y - Constants.MIN_DELTA_POSITION > wanted_y:
            self.player.set_y(self.player.y - Constants.MIN_DELTA_POSITION)
        elif cur_y + Constants.MIN_DELTA_POSITION < wanted_y:
            self.player.set_y(self.player.y + Constants.MIN_DELTA_POSITION)

        if (
                cur_x + Constants.MIN_DELTA_POSITION_DOUBLE > wanted_x > cur_x - Constants.MIN_DELTA_POSITION_DOUBLE and
                cur_y + Constants.MIN_DELTA_POSITION_DOUBLE > wanted_y > cur_y - Constants.MIN_DELTA_POSITION_DOUBLE
        ):
            self.path.pop()
        else:
            wanted_angle = math.degrees(d_r)
            wanted_angle %= 360

            if cur_angle - Constants.MIN_DELTA_ANGLE * 3 > wanted_angle:
                self.player.set_angle(self.player.angle - Constants.MIN_DELTA_ANGLE)
            elif cur_angle + Constants.MIN_DELTA_ANGLE * 3 < wanted_angle:
                self.player.set_angle(self.player.angle + Constants.MIN_DELTA_ANGLE)

    def activate(self):
        # during game static variables
        mini_map_offset_x = self.mini_map_offset_x
        mini_map_offset_y = self.mini_map_offset_y
        mini_map_factor = Constants.MULTIPLICATOR_MINIMAP
        game_map_size_x = self.game_map.size_x
        game_map_size_y = self.game_map.size_y
        game_map_data = self.game_map.data
        window_height = Constants.WINDOW_HEIGHT

        config_fov = self.config.fov
        config_pixel_size = self.config.pixel_size
        config_is_perspective_correction_on = self.config.is_perspective_correction_on
        config_dynamic_lighting = self.config.dynamic_lighting

        # pygame static variables
        pygame_surface = self.surface
        while 1:  # game engine ticks
            # during game changing variables
            player_angle = self.player.angle
            player_pos_x = self.player.x
            player_pos_y = self.player.y
            player_path = self.path

            canvas = pygame.PixelArray(pygame_surface)

            x_cor_ordered_z_buffer_walls, x_cor_ordered_z_buffer_objects = Raycaster.get_x_cor_ordered_z_buffer_data(
                player_angle=player_angle,
                player_pos_x=player_pos_x,
                player_pos_y=player_pos_y,
                config_fov=config_fov,
                config_pixel_size=config_pixel_size,
                config_is_perspective_correction_on=config_is_perspective_correction_on,
                mini_map_offset_x=mini_map_offset_x,
                game_map_size_x=game_map_size_x,
                game_map_size_y=game_map_size_y,
                game_map=self.game_map.data
            )
            Renderer.draw_from_z_buffer_walls(
                canvas=canvas,
                dynamic_lighting=config_dynamic_lighting,
                pixel_size=config_pixel_size,
                window_height=window_height,
                x_cor_ordered_z_buffer_data=x_cor_ordered_z_buffer_walls
            )
            Renderer.draw_from_z_buffer_objects(
                canvas=canvas,
                dynamic_lighting=config_dynamic_lighting,
                pixel_size=config_pixel_size,
                window_height=window_height,
                x_cor_ordered_z_buffer_data=x_cor_ordered_z_buffer_objects,
            )
            Renderer.draw_minimap(
                canvas=canvas,
                offset_x=mini_map_offset_x,
                offset_y=mini_map_offset_y,
                game_map_data=game_map_data,
                player_x=player_pos_x,
                player_y=player_pos_y,
                path=player_path,
                mini_map_factor=mini_map_factor
            )
            self.player.tick()  # move player
            self.clock.tick(30)  # make sure game doesn't run at more than 30 frames per second

            if self.path:  # move player if the path is set
                self.handle_path()

            if self.handle_events():
                return

            screen = pygame.display.get_surface()
            del canvas
            screen.blit(pygame_surface, (0, 0))

            fps = self.font.render(str(int(self.clock.get_fps())), True, pygame.Color('white'))
            screen.blit(fps, (0, 0))

            pygame.display.flip()
            pygame_surface.fill((0, 0, 0))
