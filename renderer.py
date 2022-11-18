import math

from constants import Constants
from renderers.linebyline import LineByLine
import pygame




class Renderer:
    pixel_data = pygame.image.load("static/textures.png")
    grass_pixel_data = pygame.image.load("static/grass.png")
    noise_y = 0
    renderer = LineByLine

    @classmethod
    def draw_minimap(cls, surface, offset_x, offset_y, game_map_data, players, player_index, selected_position, mini_map_factor):
                
        # render minimap (player, )
        # draw objects
        for id_y, y in enumerate(game_map_data):
            for id_x, x in enumerate(y):
                line = x//8
                x_row = x % 8
                surface.blit(
                    pygame.transform.scale(Renderer.pixel_data, ((256, 64))),
                    (offset_x + id_x * mini_map_factor, offset_y + id_y * mini_map_factor),
                    (x_row*32, line*32, 32, 32)
                )
        # draw player
        # player base
        for index, player in players.items():
            player_on_minimap_x = offset_x + int((-Constants.MAP_HALF_COORDINATE + player.x) * mini_map_factor)
            player_on_minimap_y = offset_y + int((-Constants.MAP_HALF_COORDINATE + player.y) * mini_map_factor)

            if player.path:
                for _, point_y, point_x in player.path:
                    x = offset_x + int(point_x * mini_map_factor)
                    y = offset_y + int(point_y * mini_map_factor)
                    cls.renderer.draw_a_path_cross(surface, x, y, Constants.COLOR_LIGHT_GRAY)

            team_color = Constants.COLOR_GREEN if player.ally else Constants.COLOR_RED
            cls.renderer.draw_a_cross(
                surface,
                player_on_minimap_x,
                player_on_minimap_y,
                Constants.COLOR_WHITE if index == player_index else team_color,
            )
            health = player.health
            red = max(0, min(255-health, 255))
            green = min(255, max(0, health*3))
            health_bar_color = (red, green, 0)
            pygame.draw.line(
                surface,
                Constants.COLOR_BLACK,
                (
                    player_on_minimap_x,
                    player_on_minimap_y
                ),
                (
                    player_on_minimap_x + int(Constants.MULTIPLICATOR_MINIMAP),
                    player_on_minimap_y
                ), 12
            )
            pygame.draw.line(
                surface,
                health_bar_color,
                (
                    player_on_minimap_x+2, # black border on the left
                    player_on_minimap_y
                ),
                (
                    player_on_minimap_x + int(
                        Constants.MULTIPLICATOR_MINIMAP * player.health / 100
                    )-2, # black border on the right
                    player_on_minimap_y
                ), 6
            )

        if selected_position:
            cls.renderer.draw_a_cross(
                surface,
                2+offset_x + selected_position[0] * mini_map_factor,
                2+offset_y + selected_position[1] * mini_map_factor,
                Constants.COLOR_BLUE
            )

    @classmethod
    def draw_from_z_buffer_objects(cls, player_angle, surface, dynamic_lighting, pixel_size, window_height, x_cor_ordered_z_buffer_data):
        half_window_height = window_height / 2
        double_window_height = window_height * 2
        for screen_x, z_buffer_wall in x_cor_ordered_z_buffer_data:
            last_floor_position = None
            last_ceiling_position = None
            last_offset_x = 0
            last_offset_y = 0
            for entry in reversed(z_buffer_wall):

                # actual line by line rendering of the visible object
                object_distance, object_id, offset_x, offset_y, ray_x, ray_y, object_type, ray_angle = entry
                if object_distance < 0.01:
                    object_distance = 0.01
                start = int(half_window_height - window_height / (object_distance * 2))
                wall_vertical_length_full = double_window_height / (object_distance * 2)

                size_of_texture_pixel = int(wall_vertical_length_full / 64)
                one_artificial_pixel_size = size_of_texture_pixel if size_of_texture_pixel > 0 else 1

                last_pixel_position = None

                if last_ceiling_position == None:
                    last_ceiling_position = 0

                if last_floor_position == None:
                    last_floor_position = window_height

                texture_start_x = ray_x * 48 % 64  # TODO
                texture_start_y = ray_y * 48 % 64
                texture_start_x_delta = texture_start_x - last_offset_x
                texture_start_y_delta = texture_start_y - last_offset_y
                if object_type != 2:  # skip only for walls
                    # draw ceiling and floor


                    y_ceiling_start = max(0, start)
                    y_ceiling_end = min(half_window_height, last_ceiling_position)
                    ceiling_pos_delta = y_ceiling_end - y_ceiling_start
                    color = max(0, min(255, int(255 - abs(object_distance * 30))))
                    x = 0
                    for position_move in range(y_ceiling_start, y_ceiling_end, pixel_size):
                        x_cor_texture = last_offset_x + texture_start_x_delta / ceiling_pos_delta * x * pixel_size
                        y_cor_texture = last_offset_y + texture_start_y_delta / ceiling_pos_delta * x * pixel_size
                        x += 1
                        if x_cor_texture <= 1:
                            x_cor_texture = 1

                        if y_cor_texture <= 1:
                            y_cor_texture = 1

                        x_cor_texture = max(0, min(x_cor_texture, 511))
                        y_cor_texture = max(0, min(y_cor_texture, 127))
                        red, green, blue, alpha = cls.grass_pixel_data.get_at((int(x_cor_texture), int(y_cor_texture)))

                        # ceiling
                        pygame.draw.line(surface, (0, 0, blue), (screen_x, position_move),
                                         (
                                             screen_x, position_move + pixel_size),
                                         pixel_size)

                    # FLOOR
                    tile_pos_start = max(half_window_height, last_floor_position)
                    tile_pos_end = min(window_height, int(start + wall_vertical_length_full))
                    tile_pos_delta = tile_pos_end - tile_pos_start

                    x = 0
                    for position_move in range(tile_pos_start, tile_pos_end, pixel_size):
                        x_cor_texture = last_offset_x + texture_start_x_delta / tile_pos_delta * x * pixel_size
                        y_cor_texture = last_offset_y + texture_start_y_delta / tile_pos_delta * x * pixel_size
                        x += 1
                        if x_cor_texture <= 1:
                            x_cor_texture = 1

                        if y_cor_texture <= 1:
                            y_cor_texture = 1

                        x_cor_texture = max(0, min(x_cor_texture, 511))
                        y_cor_texture = max(0, min(y_cor_texture, 127))
                        red, green, blue, alpha = cls.grass_pixel_data.get_at((int(x_cor_texture), int(y_cor_texture)))

                        # floor
                        pygame.draw.line(surface, (red, green, blue), (screen_x, position_move),
                                         (
                                             screen_x, position_move + pixel_size),
                                         pixel_size)

                if object_type != 3:  # for walls and objects  # and object_distance > 0.4
                    object_id_with_offset = object_id + offset_x + offset_y
                    for vertical_wall_pixel in range(0, int(wall_vertical_length_full), one_artificial_pixel_size):
                        y_cor_texture = int(64 / wall_vertical_length_full * vertical_wall_pixel)
                        if object_type == 2:
                            y_cor_texture += 64
                        x_cor_texture = int(object_id_with_offset * 64)

                        if x_cor_texture <= 1:
                            x_cor_texture = 1

                        x_cor_texture = max(0, min(x_cor_texture, 511))
                        y_cor_texture = max(0, min(y_cor_texture, 127))
                        red, green, blue, alpha = cls.pixel_data.get_at((x_cor_texture, y_cor_texture))

                        current_pixel_position = start + vertical_wall_pixel
                        if green > 0:

                            if dynamic_lighting:
                                distance_dark_blue = int(object_distance * 3)
                                distance_dark = distance_dark_blue * 2
                                red -= distance_dark if red > distance_dark else red
                                green -= distance_dark if green > distance_dark else green
                                blue -= distance_dark_blue if blue > distance_dark_blue else blue

                            result_color_tuple = (red, green, blue)

                            for y in range(int(last_pixel_position if last_pixel_position else current_pixel_position + 1),
                                           int(current_pixel_position)):
                                if y < 0 or y > window_height:
                                    continue
                                # walls
                                pygame.draw.line(surface, result_color_tuple, (screen_x, y),
                                                 (
                                                     screen_x, y + pixel_size),
                                                 pixel_size)
                        last_pixel_position = current_pixel_position

                last_ceiling_position = start
                last_floor_position = int(start + wall_vertical_length_full)
                last_offset_x, last_offset_y = texture_start_x, texture_start_y


    @classmethod
    def draw_disabled_screen(cls, surface, pixel_size, window_width, window_height):
        gradient_range=10
        position_of_scanning_line_y = cls.noise_y
        cls.noise_y += 2
        if cls.noise_y > window_height:
            cls.noise_y = gradient_range

        for y in range(gradient_range):
            pygame.draw.line(surface, (
                0,
                255-y*25,
                0
            ), (0, position_of_scanning_line_y - y), (window_width, position_of_scanning_line_y - y), 1)
