from constants import Constants
import pygame


class LineByLine:
    @classmethod
    def draw_a_square(cls, surface, x, y, color):
        square = pygame.Rect(
            (x + 1, y + 1),
            (Constants.MULTIPLICATOR_MINIMAP - 1, Constants.MULTIPLICATOR_MINIMAP - 1)
        )
        pygame.draw.rect(surface, color, square)

    @classmethod
    def draw_a_cross(cls, surface, x, y, color):
        pygame.draw.line(surface, color, (x+5, y+5),
                         (x + Constants.MULTIPLICATOR_MINIMAP-5, y + Constants.MULTIPLICATOR_MINIMAP-5), 3)

        pygame.draw.line(surface, color, (x+5, y + Constants.MULTIPLICATOR_MINIMAP-5),
                         (x + Constants.MULTIPLICATOR_MINIMAP-5, y+5), 3)

    @classmethod
    def draw_a_path_cross(cls, surface, x, y, color):
        # vertical
        pygame.draw.line(surface, color, (x + Constants.MULTIPLICATOR_MINIMAP_HALF, y),
                         (x + Constants.MULTIPLICATOR_MINIMAP_HALF, y + Constants.MULTIPLICATOR_MINIMAP), 1)
        # horizontal
        pygame.draw.line(surface, color, (x, y + Constants.MULTIPLICATOR_MINIMAP_HALF),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y + Constants.MULTIPLICATOR_MINIMAP_HALF), 1)
