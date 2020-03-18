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

    def __init__(self, players, game_map, config):
        # constructor injection
        self.players = players
        self.round_of_units = []
        self.player_index = None
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

    def handle_events(self, selected_player):
        mouse_button_left, mouse_button_middle, mouse_button_right = pygame.mouse.get_pressed()
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
        cor_in_map_x = (mouse_pos_x - self.mini_map_offset_x) / Constants.MULTIPLICATOR_MINIMAP
        cor_in_map_y = mouse_pos_y / Constants.MULTIPLICATOR_MINIMAP
        cor_in_map_x_flat = int(cor_in_map_x)
        cor_in_map_y_flat = int(cor_in_map_y)

        if mouse_button_left:
            for player_index, player in enumerate(self.round_of_units):
                if (
                        cor_in_map_x - Constants.MAP_HALF_COORDINATE < player.x < cor_in_map_x + Constants.MAP_HALF_COORDINATE and
                        cor_in_map_y - Constants.MAP_HALF_COORDINATE < player.y < cor_in_map_y + Constants.MAP_HALF_COORDINATE
                ):
                    self.player_index = player_index
                    break
            else:
                self.player_index = None  # no player found at this position


        if mouse_button_right and selected_player is not None:
            if (
                    self.game_map.get_at(cor_in_map_x_flat, cor_in_map_y_flat) == -1 and
                    mouse_pos_x > self.mini_map_offset_x
            ):
                if selected_player.path:
                    selected_player.path.clear()
                dijkstra = Dijkstra(
                    self.game_map.data,
                    (int(selected_player.x), int(selected_player.y)),
                    (cor_in_map_x_flat, cor_in_map_y_flat)
                )
                try:
                    dijkstra.start()
                    selected_player.path = dijkstra.get_shortest_path()
                except ValueError:
                    _logger.error('Road must be selected, not wall.')
                except KeyError:
                    traceback.print_exc(file=sys.stdout)
                except IndexError:
                    traceback.print_exc(file=sys.stdout)

        for event in pygame.event.get():
            if event.type == pylocs.QUIT:
                return True
            elif event.type == pylocs.KEYDOWN and selected_player is not None:
                if event.key == pylocs.K_w:
                    selected_player.set_velocity_x(selected_player.velocity_x + math.cos(math.radians(selected_player.angle)) / 5)
                    selected_player.set_velocity_y(selected_player.velocity_y + math.sin(math.radians(selected_player.angle)) / 5)

                if event.key == pylocs.K_s:
                    selected_player.set_velocity_x(selected_player.velocity_x - math.cos(math.radians(selected_player.angle)) / 5)
                    selected_player.set_velocity_y(selected_player.velocity_y - math.sin(math.radians(selected_player.angle)) / 5)

                if event.key == pylocs.K_d:
                    selected_player.set_velocity_angle(selected_player.velocity_angle + 5)

                if event.key == pylocs.K_a:
                    selected_player.set_velocity_angle(selected_player.velocity_angle - 5)

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

    def activate(self):
        # during game static variables
        mini_map_offset_x = self.mini_map_offset_x
        mini_map_offset_y = self.mini_map_offset_y
        mini_map_factor = Constants.MULTIPLICATOR_MINIMAP
        game_map_size_x = self.game_map.size_x
        game_map_size_y = self.game_map.size_y
        game_map_data = self.game_map.data
        window_width = Constants.WINDOW_WIDTH
        window_height = Constants.WINDOW_HEIGHT

        config_fov = self.config.fov
        config_pixel_size = self.config.pixel_size
        config_is_perspective_correction_on = self.config.is_perspective_correction_on
        config_dynamic_lighting = self.config.dynamic_lighting

        self.round_of_units = []

        # prepare units for first round
        for id in range(10):
            player = self.players.acquire()

            if player.path:
                player.path.clear()
            dijkstra = Dijkstra(
                self.game_map.data,
                (int(player.x), int(player.y)),
                (17, 18)
            )
            try:
                dijkstra.start()
                player.path = dijkstra.get_shortest_path()
            except ValueError:
                _logger.error('Road must be selected, not wall.')
            except KeyError:
                traceback.print_exc(file=sys.stdout)
            except IndexError:
                traceback.print_exc(file=sys.stdout)

            self.round_of_units.append(player)


        # pygame static variables
        pygame_surface = self.surface
        while 1:  # game engine ticks
            # during game changing variables
            player_pos_x = None
            player_pos_y = None
            player_path = None
            player_index = self.player_index

            selected_player = self.round_of_units[self.player_index] if self.player_index is not None else None  # type: Player

            if self.handle_events(selected_player):
                return

            for player in self.round_of_units:
                player.tick(game_map_data)

            canvas = pygame.PixelArray(pygame_surface)
            if selected_player:
                player_angle = selected_player.angle
                player_pos_x = selected_player.x
                player_pos_y = selected_player.y

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
                    game_map=game_map_data
                )
                Renderer.draw_from_z_buffer_walls(
                    canvas=canvas,
                    dynamic_lighting=config_dynamic_lighting,
                    pixel_size=config_pixel_size,
                    window_height=window_height / 3,
                    x_cor_ordered_z_buffer_data=x_cor_ordered_z_buffer_walls
                )
                Renderer.draw_from_z_buffer_objects(
                    canvas=canvas,
                    dynamic_lighting=config_dynamic_lighting,
                    pixel_size=config_pixel_size,
                    window_height=window_height / 3,
                    x_cor_ordered_z_buffer_data=x_cor_ordered_z_buffer_objects,
                )
            else:
                Renderer.draw_noise(
                    canvas=canvas,
                    pixel_size=config_pixel_size,
                    window_width=int(mini_map_offset_x),
                    window_height=int(window_height / 3)
                )
            Renderer.draw_minimap(
                canvas=canvas,
                offset_x=mini_map_offset_x,
                offset_y=mini_map_offset_y,
                game_map_data=game_map_data,
                players=self.round_of_units,
                player_index=self.player_index,
                mini_map_factor=mini_map_factor
            )

            self.clock.tick(30)  # make sure game doesn't run at more than 30 frames per second

            screen = pygame.display.get_surface()
            del canvas
            screen.blit(pygame_surface, (0, 0))
            text_list = []
            text_list.append('FPS: ')
            text_list.append(str(int(self.clock.get_fps())))
            fps = self.font.render(' '.join(text_list), True, pygame.Color('white'))
            screen.blit(fps, (0, window_height/3))

            pygame.display.flip()
            pygame_surface.fill((0, 0, 0))
