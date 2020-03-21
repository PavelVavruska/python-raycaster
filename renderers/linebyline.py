from constants import Constants
import pygame


class LineByLine:
    @classmethod
    def draw_a_squere(cls, canvas, x, y, color):
        squere = pygame.Rect((x, y), (x + Constants.MULTIPLICATOR_MINIMAP, y + Constants.MULTIPLICATOR_MINIMAP))
        pygame.draw.rect(canvas, color, squere)
        """# top
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
            canvas[x + Constants.MULTIPLICATOR_MINIMAP - 2, y + pixel_of_line] = color"""

    @classmethod
    def draw_a_cross(cls, canvas, x, y, color):
        pygame.draw.line(canvas, color, (x, y),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y + Constants.MULTIPLICATOR_MINIMAP), 1)

        pygame.draw.line(canvas, color, (x, y + Constants.MULTIPLICATOR_MINIMAP),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y), 1)
        '''# top
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 1):
            canvas[x + Constants.MULTIPLICATOR_MINIMAP - pixel_of_line, y + pixel_of_line] = color
        # bottom
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 1):
            canvas[x + pixel_of_line, y + pixel_of_line] = color'''

    @classmethod
    def draw_a_path_cross(cls, canvas, x, y, color):
        # vertical
        pygame.draw.line(canvas, color, (x + Constants.MULTIPLICATOR_MINIMAP_HALF, y),
                         (x + Constants.MULTIPLICATOR_MINIMAP_HALF, y + Constants.MULTIPLICATOR_MINIMAP), 1)
        # horizontal
        pygame.draw.line(canvas, color, (x, y + Constants.MULTIPLICATOR_MINIMAP_HALF),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y + Constants.MULTIPLICATOR_MINIMAP_HALF), 1)
        ''''# bottom
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 2):
            canvas[x + pixel_of_line, y + Constants.MULTIPLICATOR_MINIMAP_HALF] = color
        # left
        for pixel_of_line in range(1, Constants.MULTIPLICATOR_MINIMAP - 2):
            canvas[x + Constants.MULTIPLICATOR_MINIMAP_HALF, y + pixel_of_line] = color        '''
