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

from typing import TYPE_CHECKING

from mathematics.graph.nodes import Dijkstra
from constants import Constants
from renderer import Renderer
from mathematics.raycasting.raycaster import Raycaster

if TYPE_CHECKING:
    from models.player import Player
    from models.map import Map

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Engine:

    def __init__(self, players, game_map, config):
        # constructor injection
        self.players = players
        self.round_of_units = []
        self.player_index = None
        self.game_map = game_map  # type: Map
        self.config = config

        # game stats
        self.health = 100
        self.engine_tick = 1
        self.engine_level = 1

        # map
        self.selected_position = None  # e.g.(3, 2)

        # mobs
        self.foes_begin = (3, 2)
        self.foes_end = (17, 18)

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
                    self.selected_position = None
                    break
            else:
                self.player_index = None  # no player found at this position
                self.selected_position = (cor_in_map_x_flat, cor_in_map_y_flat)


        if mouse_button_right and selected_player is not None:
            if (
                    self.game_map.get_at(cor_in_map_x_flat, cor_in_map_y_flat) == -1 and
                    mouse_pos_x > self.mini_map_offset_x
            ):
                self.update_path_for_unit(
                    selected_player,
                    (int(selected_player.x), int(selected_player.y)),
                    (cor_in_map_x_flat, cor_in_map_y_flat)
                )

        for event in pygame.event.get():
            if event.type == pylocs.QUIT:
                return True
            elif event.type == pylocs.KEYDOWN:
                if event.key == pylocs.K_g and self.selected_position is not None:
                    position_x, position_y = self.selected_position
                    if self.game_map.get_at(position_x, position_y) <= 0:
                        self.game_map.set_at(position_x, position_y, 6)
                    units_with_changed_path = self.get_all_units_affected_by_change(self.round_of_units, (position_x, position_y), False)
                    self.update_path_for_units(units_with_changed_path)
                    self.update_effects_on_map(self.selected_position, deleted=False)

                if event.key == pylocs.K_h and self.selected_position is not None:
                    position_x, position_y = self.selected_position
                    if self.game_map.get_at(position_x, position_y) == 6:
                        self.game_map.set_at(position_x, position_y, -1)
                    units_with_changed_path = self.get_all_units_affected_by_change(self.round_of_units, (position_x, position_y), True)
                    self.update_path_for_units(units_with_changed_path)
                    self.update_effects_on_map(self.selected_position, deleted=True)

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

                if selected_player is not None:
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

        return False

    @classmethod
    def get_all_units_affected_by_change(cls, all_units, changed_map_position, change_to_empty):
        if change_to_empty:
            return all_units
        # if changed to wall, recalculate only if the wall is on the path
        units_to_update = []
        for unit in all_units:  # type: Player
            unit_path = unit.path
            if unit_path is not None:
                for _, point_position_y, point_position_x in unit_path:
                    if (point_position_x, point_position_y) == changed_map_position:
                        units_to_update.append(unit)
                        break
        return units_to_update

    def update_path_for_units(self, all_units):
        for unit in all_units:
            self.update_path_for_unit(unit)

    def update_path_for_unit_from_begin(self, unit):
        begin_x, begin_y = self.foes_begin
        unit.set_x(begin_x)
        unit.set_y(begin_y)
        self.update_path_for_unit(unit)

    def update_path_for_unit(self, unit, start_coordinates=None, end_coordinates=None):
        if unit.path:
            unit.path.clear()

        if start_coordinates is None:
            start_coordinates=(int(unit.x), int(unit.y))
        if end_coordinates is None:
            end_coordinates=self.foes_end

        dijkstra = Dijkstra(
            self.game_map.data,
            start_coordinates,
            end_coordinates
        )
        try:
            dijkstra.start()
            unit.path = dijkstra.get_shortest_path()
        except ValueError:
            _logger.error('Road must be selected, not wall.')
        except KeyError:
            traceback.print_exc(file=sys.stdout)
        except IndexError:
            traceback.print_exc(file=sys.stdout)


    def activate(self):
        # during game static variables
        mini_map_offset_x = self.mini_map_offset_x
        mini_map_offset_y = self.mini_map_offset_y
        mini_map_factor = Constants.MULTIPLICATOR_MINIMAP
        game_map_size_x = self.game_map.size_x
        game_map_size_y = self.game_map.size_y
        game_map_data = self.game_map.data
        game_map_effect_data = self.game_map.effect_data
        window_width = Constants.WINDOW_WIDTH
        window_height = Constants.WINDOW_HEIGHT

        config_fov = self.config.fov
        config_pixel_size = self.config.pixel_size
        config_is_perspective_correction_on = self.config.is_perspective_correction_on
        config_dynamic_lighting = self.config.dynamic_lighting

        self.round_of_units = []
        # pygame static variables
        pygame_surface = self.surface
        while 1:  # game engine ticks
            self.engine_tick+=1

            if self.engine_tick > 100:
                self.engine_level += 1
                self.engine_tick = 1
                # prepare units for first round
                for _ in range(self.engine_level):
                    player = self.players.acquire()
                    if player is None:
                        break
                    self.update_health_to_max(player)
                    self.update_path_for_unit_from_begin(player)
                    self.round_of_units.append(player)
            if self.health < 1:
                # gameover
                self.health = 100
                self.engine_level = 1

            # during game changing variables
            player_pos_x = None
            player_pos_y = None
            player_path = None
            player_index = self.player_index

            selected_player = self.round_of_units[self.player_index] if self.player_index is not None else None  # type: Player

            if self.handle_events(selected_player):
                return

            players_to_delete = []
            for player in self.round_of_units:
                is_dead = player.tick(game_map_data, game_map_effect_data)
                if (int(player.x), int(player.y)) == self.foes_end:
                    self.health -= 1
                    is_dead = True
                if is_dead:
                    self.players.release(player)
                    players_to_delete.append(player)

            for player in players_to_delete:
                self.round_of_units.remove(player)

            #canvas = pygame.PixelArray(pygame_surface)
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
                    surface=pygame_surface,
                    dynamic_lighting=config_dynamic_lighting,
                    pixel_size=config_pixel_size,
                    window_height=window_height / 3,
                    x_cor_ordered_z_buffer_data=x_cor_ordered_z_buffer_walls
                )
                Renderer.draw_from_z_buffer_objects(
                    surface=pygame_surface,
                    dynamic_lighting=config_dynamic_lighting,
                    pixel_size=config_pixel_size,
                    window_height=window_height / 3,
                    x_cor_ordered_z_buffer_data=x_cor_ordered_z_buffer_objects,
                )
            else:
                Renderer.draw_disabled_screen(
                    surface=pygame_surface,
                    pixel_size=config_pixel_size,
                    window_width=int(mini_map_offset_x),
                    window_height=int(window_height / 3)
                )
            Renderer.draw_minimap(
                surface=pygame_surface,
                offset_x=mini_map_offset_x,
                offset_y=mini_map_offset_y,
                game_map_data=game_map_data,
                players=self.round_of_units,
                player_index=self.player_index,
                selected_position=self.selected_position,
                mini_map_factor=mini_map_factor
            )

            self.clock.tick(30)  # make sure game doesn't run at more than 30 frames per second

            screen = pygame.display.get_surface()

            screen.blit(pygame_surface, (0, 0))
            text_list = []
            text_list.append('FPS: ')
            text_list.append(str(int(self.clock.get_fps())))
            fps = self.font.render(' '.join(text_list), True, pygame.Color('white'))
            health_list = []
            health_list.append('Health: ')
            health_list.append(str(self.health))
            health_list.append('Level: ')
            health_list.append(str(self.engine_level))
            health_list.append('Tick: ')
            health_list.append(str(self.engine_tick))
            health = self.font.render(' '.join(health_list), True, pygame.Color('white'))
            screen.blit(fps, (0, window_height/3))
            screen.blit(health, (0, window_height / 3 + 40))
            pygame.display.flip()
            pygame_surface.fill((0, 0, 0))

    def update_effects_on_map(self, position, deleted=False):
        pos_x, pos_y = position
        effect = 1 if deleted else -1
        for y in range(pos_y-1, pos_y+1):
            for x in range(pos_x - 1, pos_x + 1):
                original_effect = self.game_map.get_effect_at(x,y)
                new_effect = original_effect + effect
                if effect <= 0:
                    self.game_map.set_effect_at(x, y, new_effect)

    def update_health_to_max(self, player):
        player.health = 100*self.engine_level


