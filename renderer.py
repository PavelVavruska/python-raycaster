from constants import Constants
from PIL import Image


class Renderer:
    texture = Image.open("static/textures.png")
    pixel_data = texture.load()

    @classmethod
    def draw_a_squere(cls, canvas, x, y, color):
        # top
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 2):
            canvas[x + pixel_of_line, y] = color
        # bottom
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 2):
            canvas[x + pixel_of_line, Constants.MULTIPLICATOR_MINIMAP - 2 + y] = color
        # left
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 2):
            canvas[x, y + pixel_of_line] = color
        # right
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 2):
            canvas[x + Constants.MULTIPLICATOR_MINIMAP - 2, y + pixel_of_line] = color

    @classmethod
    def draw_a_cross(cls, canvas, x, y, color):
        # top
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 1):
            canvas[x + Constants.MULTIPLICATOR_MINIMAP - pixel_of_line, y + pixel_of_line] = color
        # bottom
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 1):
            canvas[x + pixel_of_line, y + pixel_of_line] = color

    @classmethod
    def draw_minimap(cls, canvas, offset_x, offset_y, game_map, player, path):

        # render minimap (player, )
        # draw objects
        for id_y, y in enumerate(game_map.data):
            for id_x, x in enumerate(y):
                if x < 0:
                    color = Constants.COLOR_GRAY
                elif 0 <= x < 9:
                    color = Constants.COLOR_RED
                else:
                    color = Constants.COLOR_GREEN
                cls.draw_a_squere(
                    canvas,
                    offset_x + id_x * Constants.MULTIPLICATOR_MINIMAP,
                    offset_y + id_y * Constants.MULTIPLICATOR_MINIMAP,
                    color
                )

        # draw player
        # player base
        player_on_minimap_x = offset_x + int((-Constants.MAP_HALF_COORDINATE + player.x) * Constants.MULTIPLICATOR_MINIMAP)
        player_on_minimap_y = offset_y + int((-Constants.MAP_HALF_COORDINATE + player.y) * Constants.MULTIPLICATOR_MINIMAP)

        cls.draw_a_cross(canvas, player_on_minimap_x, player_on_minimap_y, Constants.COLOR_WHITE)

        if path:
            for _, point_y, point_x in path:
                x = offset_x + int(point_x * Constants.MULTIPLICATOR_MINIMAP)
                y = offset_y + int(point_y * Constants.MULTIPLICATOR_MINIMAP)
                cls.draw_a_cross(canvas, x, y, Constants.COLOR_YELLOW)

    @classmethod
    def draw_from_z_buffer_wall(cls, canvas, config, z_buffer_wall, screen_x):


        for entry in sorted(z_buffer_wall, reverse=True):
            # actual line by line rendering of the visible object
            object_distance, object_id = entry
            if object_distance < 0.2:  # skip render distance is too short
                continue
            start = int(Constants.WINDOW_HEIGHT / 2 - Constants.WINDOW_HEIGHT / (object_distance * 2))
            wall_vertical_length_full = 2 * Constants.WINDOW_HEIGHT / (object_distance * 2)

            size_of_texture_pixel = int(wall_vertical_length_full / 64)
            one_artificial_pixel_size = size_of_texture_pixel if size_of_texture_pixel > 0 else 1

            last_pixel_position = None
            for vertical_wall_pixel in range(0, int(wall_vertical_length_full), one_artificial_pixel_size):
                y_cor_texture = int(64 + 64 / wall_vertical_length_full * vertical_wall_pixel)
                x_cor_texture = int(object_id * 64)

                if x_cor_texture <= 1:
                    x_cor_texture = 1

                red, green, blue, alpha = cls.pixel_data[x_cor_texture, y_cor_texture]
                if config.dynamic_lighting:
                    distance_dark_blue = int(object_distance * 3)
                    distance_dark = distance_dark_blue * 2
                    red -= distance_dark if red > distance_dark else red
                    green -= distance_dark if green > distance_dark else green
                    blue -= distance_dark_blue if blue > distance_dark_blue else blue

                result_color_string = (red, green, blue)

                current_pixel_position = start + vertical_wall_pixel
                for y in range(int(last_pixel_position if last_pixel_position else current_pixel_position + 1),
                               int(current_pixel_position)):
                    for a in range(config.pixel_size):
                        real_x = screen_x + a
                        if 0 < y < Constants.WINDOW_HEIGHT:
                            canvas[real_x, y] = result_color_string
                last_pixel_position = current_pixel_position
            break