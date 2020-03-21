from constants import Constants
import pygame


class LineByLine:
    @classmethod
    def draw_a_squere(cls, canvas, x, y, color):
        squere = pygame.Rect(
            (x + 1, y + 1),
            (Constants.MULTIPLICATOR_MINIMAP - 1, Constants.MULTIPLICATOR_MINIMAP - 1)
        )
        pygame.draw.rect(canvas, color, squere)

    @classmethod
    def draw_a_cross(cls, canvas, x, y, color):
        pygame.draw.line(canvas, color, (x, y),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y + Constants.MULTIPLICATOR_MINIMAP), 1)

        pygame.draw.line(canvas, color, (x, y + Constants.MULTIPLICATOR_MINIMAP),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y), 1)

    @classmethod
    def draw_a_path_cross(cls, canvas, x, y, color):
        # vertical
        pygame.draw.line(canvas, color, (x + Constants.MULTIPLICATOR_MINIMAP_HALF, y),
                         (x + Constants.MULTIPLICATOR_MINIMAP_HALF, y + Constants.MULTIPLICATOR_MINIMAP), 1)
        # horizontal
        pygame.draw.line(canvas, color, (x, y + Constants.MULTIPLICATOR_MINIMAP_HALF),
                         (x + Constants.MULTIPLICATOR_MINIMAP, y + Constants.MULTIPLICATOR_MINIMAP_HALF), 1)
