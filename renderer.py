from constants import Constants
from PIL import Image
from renderers.linebyline import LineByLine
import pygame


class Renderer:
    texture = Image.open("static/textures.png")
    pixel_data = texture.load()
    noise_y = 0
    renderer = LineByLine

    @classmethod
    def draw_minimap(cls, surface, offset_x, offset_y, game_map_data, players, player_index, selected_position, mini_map_factor):

        # render minimap (player, )
        # draw objects
        for id_y, y in enumerate(game_map_data):
            for id_x, x in enumerate(y):
                if x < 0:
                    color = Constants.COLOR_GRAY
                elif x < 6:
                    color = Constants.COLOR_RED
                elif x == 6:
                    color = Constants.COLOR_WHITE
                else:
                    color = Constants.COLOR_GREEN
                cls.renderer.draw_a_squere(
                    surface,
                    offset_x + id_x * mini_map_factor,
                    offset_y + id_y * mini_map_factor,
                    color
                )

        # draw player
        # player base
        for index, player in enumerate(players):
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
                Constants.COLOR_WHITE if index == player_index else team_color
            )

        if selected_position:
            cls.renderer.draw_a_cross(
                surface,
                2+offset_x + selected_position[0] * mini_map_factor,
                2+offset_y + selected_position[1] * mini_map_factor,
                Constants.COLOR_BLUE
            )



    @classmethod
    def draw_from_z_buffer_walls(cls, surface, dynamic_lighting, pixel_size, window_height, x_cor_ordered_z_buffer_data):
        half_window_height = window_height / 2
        double_window_height = window_height * 2
        for screen_x, z_buffer_wall in x_cor_ordered_z_buffer_data:
            for entry in z_buffer_wall:
                # actual line by line rendering of the visible object
                object_distance, object_id = entry
                if object_distance < 0.2:  # skip render distance is too short
                    continue
                start = int(half_window_height - window_height / (object_distance * 2))
                wall_vertical_length_full = double_window_height / (object_distance * 2)

                size_of_texture_pixel = int(wall_vertical_length_full / 64)
                one_artificial_pixel_size = size_of_texture_pixel if size_of_texture_pixel > 0 else 1

                last_pixel_position = None
                for vertical_wall_pixel in range(0, int(wall_vertical_length_full), one_artificial_pixel_size):
                    y_cor_texture = int(64 + 64 / wall_vertical_length_full * vertical_wall_pixel)
                    x_cor_texture = int(object_id * 64)

                    if x_cor_texture <= 1:
                        x_cor_texture = 1

                    red, green, blue, alpha = cls.pixel_data[x_cor_texture, y_cor_texture]
                    if dynamic_lighting:
                        distance_dark_blue = int(object_distance * 3)
                        distance_dark = distance_dark_blue * 2
                        red -= distance_dark if red > distance_dark else red
                        green -= distance_dark if green > distance_dark else green
                        blue -= distance_dark_blue if blue > distance_dark_blue else blue

                    result_color_tuple = (red, green, blue)

                    current_pixel_position = start + vertical_wall_pixel
                    for y in range(int(last_pixel_position if last_pixel_position else current_pixel_position + 1),
                                   int(current_pixel_position)):
                        pygame.draw.line(surface, result_color_tuple, (screen_x, y),
                                         (
                                         screen_x, y + pixel_size),
                                         2)
                        #for a in range(pixel_size):
                        #    real_x = screen_x + a
                        #    if 0 < y < window_height:
                        #        surface[real_x, y] = result_color_tuple
                    last_pixel_position = current_pixel_position
                break

    @classmethod
    def draw_from_z_buffer_objects(cls, surface, dynamic_lighting, pixel_size, window_height, x_cor_ordered_z_buffer_data):
        half_window_height = window_height / 2
        double_window_height = window_height * 2
        for screen_x, z_buffer_wall in x_cor_ordered_z_buffer_data:
            for entry in reversed(z_buffer_wall):
                # actual line by line rendering of the visible object
                object_distance, object_id = entry
                if object_distance < 0.2:  # skip render distance is too short
                    continue
                start = int(half_window_height - window_height / (object_distance * 2))
                wall_vertical_length_full = double_window_height / (object_distance * 2)

                size_of_texture_pixel = int(wall_vertical_length_full / 64)
                one_artificial_pixel_size = size_of_texture_pixel if size_of_texture_pixel > 0 else 1

                last_pixel_position = None
                for vertical_wall_pixel in range(0, int(wall_vertical_length_full), one_artificial_pixel_size):
                    y_cor_texture = int(64 / wall_vertical_length_full * vertical_wall_pixel)
                    x_cor_texture = int(object_id * 64)

                    if x_cor_texture <= 1:
                        x_cor_texture = 1

                    red, green, blue, alpha = cls.pixel_data[x_cor_texture, y_cor_texture]

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
                            pygame.draw.line(surface, result_color_tuple, (screen_x, y),
                                             (
                                                 screen_x, y + pixel_size),
                                             2)
                    last_pixel_position = current_pixel_position

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


