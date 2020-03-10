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
import logging
import math
import traceback
import pygame
import pygame.locals as pylocs

from graphmath.nodes import Dijkstra
from constants import Constants
from renderer import Renderer

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Engine:

    def __init__(self, player, game_map, config):
        self.player = player
        self.game_map = game_map
        self.config = config
        self.mini_map_offset_x = Constants.WINDOW_WIDTH - game_map.size_x * Constants.MULTIPLICATOR_MINIMAP
        self.mini_map_offset_y = 0
        pygame.init()
        self.font = pygame.font.Font(None, 30)
        self.surface = pygame.Surface((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        self.path = None

        pygame.display.set_caption('Pygame - pixel by pixel raycaster')
        self.screen = pygame.display.set_mode((Constants.WINDOW_WIDTH, Constants.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()  # initialise clock
        pygame.key.set_repeat(True)  # enable key holding

    def start(self):
        while 1:  # event loop
            on_screen_text = str(int(self.clock.get_fps()))

            canvas = pygame.PixelArray(self.surface)
            self.draw_scene(canvas)  # render graphics
            canvas = pygame.PixelArray(self.surface)
            Renderer.draw_minimap(canvas, self.mini_map_offset_x, self.mini_map_offset_y, self.game_map, self.player,
                                  self.path)  # render minimap
            self.player.tick()  # move player
            self.clock.tick(30)  # make sure game doesn't run at more than 60 frames per second

            if self.path:  # move player if the path is set
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

                int_cur_x = cur_x
                int_cur_y = cur_y
                int_wanted_x = wanted_x
                int_wanted_y = wanted_y

                if (
                        int_cur_x + Constants.MIN_DELTA_POSITION_DOUBLE > int_wanted_x > int_cur_x - Constants.MIN_DELTA_POSITION_DOUBLE and
                        int_cur_y + Constants.MIN_DELTA_POSITION_DOUBLE > int_wanted_y > int_cur_y - Constants.MIN_DELTA_POSITION_DOUBLE
                ):
                    self.path.pop()
                else:
                    wanted_angle = math.degrees(d_r)
                    if wanted_angle > 360:
                        wanted_angle -= 360
                    if wanted_angle < 0:
                        wanted_angle += 360

                    if cur_angle - Constants.MIN_DELTA_ANGLE * 3 > wanted_angle:
                        self.player.set_angle(self.player.angle - Constants.MIN_DELTA_ANGLE)
                    elif cur_angle + Constants.MIN_DELTA_ANGLE * 3 < wanted_angle:
                        self.player.set_angle(self.player.angle + Constants.MIN_DELTA_ANGLE)

            for event in pygame.event.get():
                if event.type == pylocs.QUIT:
                    return
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

            screen = pygame.display.get_surface()
            del canvas
            screen.blit(self.surface, (0, 0))

            fps = self.font.render(on_screen_text, True, pygame.Color('white'))
            screen.blit(fps, (0, 0))

            pygame.display.flip()
            self.surface.fill((0, 0, 0))

    def draw_scene(self, canvas):
        player_angle = self.player.angle
        player_angle_start = player_angle - self.config.fov / 2

        for screen_x in range(0, int(self.mini_map_offset_x), self.config.pixel_size):
            ray_angle = player_angle_start + self.config.fov / self.mini_map_offset_x * screen_x

            # degrees fixed to range 0 - 359
            if ray_angle < 0:
                ray_angle += 360
            elif ray_angle >= 360:
                ray_angle -= 360

            ray_position_x = self.player.x  # start position of ray on X axis
            ray_position_y = self.player.y  # start position of ray on Y axis

            z_buffer_wall = []
            z_buffer_object = []

            ray_position_previous_x = 0
            ray_position_previous_y = 0

            ray_time_to_die = 50

            while (0 < ray_position_x < self.game_map.size_x and
                   0 < ray_position_y < self.game_map.size_y and
                   ray_time_to_die > 0):

                ray_time_to_die -= 1

                if ray_position_previous_x == ray_position_x and ray_position_previous_y == ray_position_y:
                    # ray is dead - end its misery
                    break
                ray_position_for_map_collision_x = int(ray_position_x)

                if 90 < ray_angle < 270:
                    ray_position_for_map_collision_x = math.ceil(ray_position_x - 1)
                ray_position_for_map_collision_y = int(ray_position_y)

                if 180 < ray_angle < 360:
                    ray_position_for_map_collision_y = math.ceil(ray_position_y - 1)

                if (0 <= ray_position_for_map_collision_x < self.game_map.size_x and
                        0 <= ray_position_for_map_collision_y < self.game_map.size_y):

                    object_on_the_map_type_id = self.game_map.get_at(
                        int(ray_position_for_map_collision_y),
                        int(ray_position_for_map_collision_x)
                    )
                    ray_position_offset_from_the_object_edge = (
                            (ray_position_x - ray_position_for_map_collision_x)
                            + (ray_position_y - ray_position_for_map_collision_y)
                    )

                    object_on_the_map_type_id_with_offset = object_on_the_map_type_id + ray_position_offset_from_the_object_edge

                    if object_on_the_map_type_id != -1:  # read the map and save it to zbuffer

                        ray_distance_from_player_x = self.player.x - ray_position_x
                        ray_distance_from_player_y = self.player.y - ray_position_y
                        ray_distance_from_player = math.sqrt(
                            math.pow(ray_distance_from_player_x, 2) + math.pow(ray_distance_from_player_y, 2)
                        )
                        if object_on_the_map_type_id >= 10:  # solid walls
                            if self.config.is_perspective_correction_on:
                                ray_perspective_correction_angle = abs(ray_angle) - abs(player_angle)
                                ray_distance_from_player_with_perspective_correction = math.cos(
                                    math.radians(ray_perspective_correction_angle)
                                ) * ray_distance_from_player
                                z_buffer_wall.append(
                                    (
                                        ray_distance_from_player_with_perspective_correction,
                                        object_on_the_map_type_id_with_offset - 10
                                    )
                                )
                            else:
                                z_buffer_wall.append(
                                    (ray_distance_from_player, object_on_the_map_type_id_with_offset - 10))
                            break
                        else:  # transparent walls
                            if self.config.is_perspective_correction_on:
                                ray_perspective_correction_angle = abs(ray_angle) - abs(player_angle)
                                ray_distance_from_player_with_perspective_correction = math.cos(
                                    math.radians(ray_perspective_correction_angle)
                                ) * ray_distance_from_player
                                z_buffer_object.append(
                                    (
                                        ray_distance_from_player_with_perspective_correction,
                                        object_on_the_map_type_id_with_offset
                                    )
                                )
                            else:
                                z_buffer_object.append(
                                    (ray_distance_from_player, object_on_the_map_type_id_with_offset))

                # QUADRANTS:
                # 1
                # 0 - 90
                # 2
                # 90 - 180
                # 3
                # 180 - 270
                # 4
                # 270 - 360
                if 0 <= ray_angle <= 90:
                    ray_length_delta_x = 1 + int(ray_position_x) - ray_position_x
                    ray_length_delta_y = 1 + int(ray_position_y) - ray_position_y

                    ray_angle_to_tile_edge = math.degrees(math.atan(ray_length_delta_y / ray_length_delta_x))

                    if ray_angle_to_tile_edge >= ray_angle:
                        ray_position_x = ray_position_x + ray_length_delta_x
                        ray_position_y += math.tan(math.radians(ray_angle)) * ray_length_delta_x
                    else:
                        ray_position_x += ray_length_delta_y / math.tan(math.radians(ray_angle))
                        ray_position_y = ray_position_y + ray_length_delta_y

                elif 90 < ray_angle < 180:
                    ray_length_delta_x = 1 - int(math.ceil(ray_position_x)) + ray_position_x
                    ray_length_delta_y = 1 + int(ray_position_y) - ray_position_y
                    ray_angle_to_tile_edge = 90 + math.degrees(math.atan(ray_length_delta_x / ray_length_delta_y))

                    if ray_angle_to_tile_edge <= ray_angle:
                        ray_position_x = ray_position_x - ray_length_delta_x
                        ray_position_y += ray_length_delta_x / math.tan(math.radians(ray_angle - 90))
                    else:
                        ray_position_x -= math.tan(math.radians(ray_angle - 90)) * ray_length_delta_y
                        ray_position_y = ray_position_y + ray_length_delta_y

                elif 180 <= ray_angle < 270:
                    ray_length_delta_x = 1 - int(math.ceil(ray_position_x)) + ray_position_x
                    ray_length_delta_y = 1 - int(math.ceil(ray_position_y)) + ray_position_y
                    ray_angle_to_tile_edge = 180 + math.degrees(math.atan(ray_length_delta_y / ray_length_delta_x))

                    if ray_angle_to_tile_edge > ray_angle:
                        ray_position_x = ray_position_x - ray_length_delta_x
                        ray_position_y -= math.tan(math.radians(ray_angle - 180)) * ray_length_delta_x
                    else:
                        ray_position_x -= ray_length_delta_y / math.tan(math.radians(ray_angle - 180))
                        ray_position_y = ray_position_y - ray_length_delta_y

                elif 270 <= ray_angle < 360:
                    ray_length_delta_x = 1 + int(ray_position_x) - ray_position_x
                    ray_length_delta_y = 1 - int(math.ceil(ray_position_y)) + ray_position_y
                    ray_angle_to_tile_edge = 270 + math.degrees(math.atan(ray_length_delta_x / ray_length_delta_y))

                    if ray_angle_to_tile_edge > ray_angle:
                        ray_position_x += math.tan(math.radians(ray_angle - 270)) * ray_length_delta_y
                        ray_position_y = ray_position_y - ray_length_delta_y
                    else:
                        ray_position_x = ray_position_x + ray_length_delta_x
                        ray_position_y -= ray_length_delta_x / math.tan(math.radians(ray_angle - 270))

                ray_position_previous_x = ray_position_y
                ray_position_previous_y = ray_position_x

            #canvas = pygame.PixelArray(self.surface)
            Renderer.draw_from_z_buffer_wall(canvas, self.config, z_buffer_wall, screen_x)