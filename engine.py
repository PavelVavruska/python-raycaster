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
from PIL import Image
from models.config import Config
from models.map import Map
from models.player import Player
from graphmath.nodes import Dijkstra

# constants
BASE_WIDTH, BASE_HEIGHT = 7, 3
MULTIPLICATOR_WIDTH, MULTIPLICATOR_HEIGHT = 100, 100
WINDOW_WIDTH, WINDOW_HEIGHT = int(MULTIPLICATOR_WIDTH*BASE_WIDTH), int(MULTIPLICATOR_HEIGHT*BASE_HEIGHT)

NUMBER_OF_HORIZONTAL_BIG_PIXELS = WINDOW_WIDTH
start_frame_switcher = 0

MICROSECONDS_IN_SECOND = 1_000_000
NANOSECONDS_IN_SECOND = 1_000_000_000
MINIMAP_BASE = 3
MULTIPLICATOR_MINIMAP = 5 * MINIMAP_BASE

COLOR_WHITE = (255, 255, 255)  # '#FFFFFF'
COLOR_BLACK = (0, 0, 0)  # '#000000'
COLOR_CYAN = (0, 255, 255)  # '#0000FF'
COLOR_GREEN = (0, 255, 0)  # '#00FF00'
COLOR_RED = (255, 0, 0)  # '#FF0000'
COLOR_GRAY = (50, 50, 50)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLUE = (0, 0, 255)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

player = Player(3, 3, 100)
config = Config(
    fov=130,
    is_perspective_correction_on=True,
    is_metric_on=True,
    pixel_size=2,
    dynamic_lighting=True,
    texture_filtering=True
)
game_map = Map()

mini_map_offset_x = WINDOW_WIDTH - game_map.size_x*MULTIPLICATOR_MINIMAP
mini_map_offset_y = 0
texture = Image.open("static/textures.png")
pixel_data = texture.load()
pygame.init()

font = pygame.font.Font(None, 30)

surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

# global
path = None


def main():
    global path
    # Initialise screen
    pygame.display.set_caption('Pygame - pixel by pixel raycaster')
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()  # initialise clock
    pygame.key.set_repeat(True)  # enable key holding

    while 1:  # event loop
        on_screen_text = str(int(clock.get_fps()))
        draw_scene()  # render graphics
        draw_minimap(mini_map_offset_x, mini_map_offset_y)  # render minimap
        player.tick()  # move player
        clock.tick(30)  # make sure game doesn't run at more than 60 frames per second

        if path:  # move player if the path is set
            path_point = path.pop()
            player.set_y(path_point[1])
            player.set_x(path_point[2])

        for event in pygame.event.get():
            if event.type == pylocs.QUIT:
                return
            elif event.type == pylocs.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                cor_in_map_x = int((pos[0]-mini_map_offset_x)/MULTIPLICATOR_MINIMAP)
                cor_in_map_y = int(pos[1]/MULTIPLICATOR_MINIMAP)
                if (
                        game_map.get_at(cor_in_map_x, cor_in_map_y) == -1 and
                        pos[0] > mini_map_offset_x
                ):
                    if path:
                        path.clear()
                    dijkstra = Dijkstra(
                        game_map.data,
                        (int(player.x), int(player.y)),
                        (cor_in_map_x, cor_in_map_y)
                    )
                    try:
                        dijkstra.start()
                        path = dijkstra.get_shortest_path()
                    except ValueError:
                        _logger.error('Road must be selected, not wall.')
                    except KeyError:
                        traceback.print_exc(file=sys.stdout)
                    except IndexError:
                        traceback.print_exc(file=sys.stdout)

            elif event.type == pylocs.KEYDOWN:
                if event.key == pylocs.K_w:
                    player.set_velocity_x(player.velocity_x + math.cos(math.radians(player.angle)) / 5)
                    player.set_velocity_y(player.velocity_y + math.sin(math.radians(player.angle)) / 5)

                if event.key == pylocs.K_s:
                    player.set_velocity_x(player.velocity_x - math.cos(math.radians(player.angle)) / 5)
                    player.set_velocity_y(player.velocity_y - math.sin(math.radians(player.angle)) / 5)

                if event.key == pylocs.K_d:
                    player.set_velocity_angle(player.velocity_angle + 5)

                if event.key == pylocs.K_a:
                    player.set_velocity_angle(player.velocity_angle - 5)

                if event.key == pylocs.K_p:
                    config.toggle_perspective_correction_on()

                if event.key == pylocs.K_l:
                    config.toggle_dynamic_lighting()

                if event.key == pylocs.K_t:
                    config.toggle_texture_filtering()

                if event.key == pylocs.K_UP:
                    config.increase_pixel_size()

                if event.key == pylocs.K_DOWN:
                    config.decrease_pixel_size()

        screen = pygame.display.get_surface()
        screen.blit(surface, (0, 0))

        fps = font.render(on_screen_text, True, pygame.Color('white'))
        screen.blit(fps, (0, 0))

        pygame.display.flip()
        surface.fill((0, 0, 0))


def draw_a_squere(canvas, x, y, color):
    # top
    for pixel_of_line in range(1, MULTIPLICATOR_MINIMAP-1):
        canvas[x + pixel_of_line, y] = color
    # bottom
    for pixel_of_line in range(1, MULTIPLICATOR_MINIMAP-1):
        canvas[x + pixel_of_line, MULTIPLICATOR_MINIMAP-1 + y] = color
    # left
    for pixel_of_line in range(1, MULTIPLICATOR_MINIMAP-1):
        canvas[x, y + pixel_of_line] = color
    # right
    for pixel_of_line in range(1, MULTIPLICATOR_MINIMAP-1):
        canvas[x + MULTIPLICATOR_MINIMAP - 1, y + pixel_of_line] = color


def draw_a_cross(canvas, x, y, color):
    # top
    for pixel_of_line in range(1, MULTIPLICATOR_MINIMAP-1):
        canvas[x + MULTIPLICATOR_MINIMAP - pixel_of_line, y + pixel_of_line] = color
    # bottom
    for pixel_of_line in range(1, MULTIPLICATOR_MINIMAP-1):
        canvas[x + pixel_of_line, y + pixel_of_line] = color

def draw_minimap(offset_x, offset_y):
    __canvas = pygame.PixelArray(surface)
    # render minimap (player, )
    # draw objects
    for id_y, y in enumerate(game_map.data):
        for id_x, x in enumerate(y):
            if x < 0:
                color = COLOR_GRAY
            elif 0 <= x < 9:
                color = COLOR_RED
            else:
                color = COLOR_GREEN
            draw_a_squere(
                __canvas,
                offset_x + id_x * MULTIPLICATOR_MINIMAP,
                offset_y + id_y * MULTIPLICATOR_MINIMAP,
                color
            )

    # draw player
    # player base
    player_on_minimap_x = offset_x + int(player.x * MULTIPLICATOR_MINIMAP)
    player_on_minimap_y = offset_y + int(player.y * MULTIPLICATOR_MINIMAP)

    draw_a_squere(__canvas, player_on_minimap_x, player_on_minimap_y, COLOR_WHITE)

    if path:
        for point in path:
            x = offset_x + int(point[2] * MULTIPLICATOR_MINIMAP)
            y = offset_y + int(point[1] * MULTIPLICATOR_MINIMAP)
            draw_a_cross(__canvas, x, y, COLOR_YELLOW)


def draw_from_z_buffer_wall(z_buffer_wall, screen_x, param, param1):

    __canvas = pygame.PixelArray(surface)
    for entry in sorted(z_buffer_wall, reverse=True):
        # actual line by line rendering of the visible object
        if entry[0] < 1:
            continue
        start = int(WINDOW_HEIGHT / 2 - WINDOW_HEIGHT / (entry[0]*2))
        wall_vertical_length_full = 2 * WINDOW_HEIGHT / (entry[0]*2)

        size_of_texture_pixel = int(wall_vertical_length_full / 64)
        one_artificial_pixel_size = size_of_texture_pixel if size_of_texture_pixel>0 else 1

        last_pixel_position = None
        for vertical_wall_pixel in range(0, int(wall_vertical_length_full), one_artificial_pixel_size):
            y_cor_texture = int(64 + 64/wall_vertical_length_full*vertical_wall_pixel)
            x_cor_texture = int(entry[1] * 64)

            if x_cor_texture <= 1:
                x_cor_texture = 1

            red, green, blue, alpha = pixel_data[x_cor_texture, y_cor_texture]
            if config.dynamic_lighting:
                distance_dark_blue = int(entry[0]*3)
                distance_dark = distance_dark_blue*2
                red -= distance_dark if red > distance_dark else red
                green -= distance_dark if green > distance_dark else green
                blue -= distance_dark_blue if blue > distance_dark_blue else blue

            result_color_string = (red, green, blue)

            current_pixel_position = start + vertical_wall_pixel
            for y in range(int(last_pixel_position if last_pixel_position else current_pixel_position + 1), int(current_pixel_position)):
                for a in range(config.pixel_size):
                    __canvas[screen_x+a, y] = result_color_string
            last_pixel_position = current_pixel_position
        break
    del __canvas


def draw_scene():
    player_angle = player.angle
    player_angle_start = player_angle - config.fov / 2

    for screen_x in range(0, int(mini_map_offset_x), config.pixel_size):
        ray_angle = player_angle_start + config.fov / mini_map_offset_x * screen_x

        # degrees fixed to range 0 - 359
        if ray_angle < 0:
            ray_angle += 360
        elif ray_angle >= 360:
            ray_angle -= 360

        ray_position_x = player.x  # start position of ray on X axis
        ray_position_y = player.y  # start position of ray on Y axis

        z_buffer_wall = []
        z_buffer_object = []

        ray_position_previous_x = 0
        ray_position_previous_y = 0

        ray_time_to_die = 50

        while (0 < ray_position_x < game_map.size_x and
               0 < ray_position_y < game_map.size_y and
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

            if (0 <= ray_position_for_map_collision_x < game_map.size_x and
                    0 <= ray_position_for_map_collision_y < game_map.size_y):

                object_on_the_map_type_id = game_map.get_at(
                    int(ray_position_for_map_collision_y),
                    int(ray_position_for_map_collision_x)
                )
                ray_position_offset_from_the_object_edge = (
                        (ray_position_x - ray_position_for_map_collision_x)
                        + (ray_position_y - ray_position_for_map_collision_y)
                )

                object_on_the_map_type_id_with_offset = object_on_the_map_type_id + ray_position_offset_from_the_object_edge

                if object_on_the_map_type_id != -1:  # read the map and save it to zbuffer

                    ray_distance_from_player_x = player.x - ray_position_x
                    ray_distance_from_player_y = player.y - ray_position_y
                    ray_distance_from_player = math.sqrt(
                        math.pow(ray_distance_from_player_x, 2) + math.pow(ray_distance_from_player_y, 2)
                    )
                    if object_on_the_map_type_id >= 10:  # solid walls
                        if config.is_perspective_correction_on:
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
                            z_buffer_wall.append((ray_distance_from_player, object_on_the_map_type_id_with_offset - 10))
                        break
                    else:  # transparent walls
                        if config.is_perspective_correction_on:
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
                            z_buffer_object.append((ray_distance_from_player, object_on_the_map_type_id_with_offset))


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

        draw_from_z_buffer_wall(z_buffer_wall, screen_x, 0, 0)


if __name__ == '__main__':
    main()