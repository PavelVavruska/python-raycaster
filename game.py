from engine import Engine
from models.player import Player
from models.config import Config
from models.map import Map
from constants import Constants


def main():
    # Initialise screen
    player = Player(3, 3, 100)
    config = Config(
        fov=100,
        is_perspective_correction_on=True,
        is_metric_on=True,
        pixel_size=2,
        dynamic_lighting=True,
        texture_filtering=True
    )
    game_map = Map()
    engine = Engine(player=player, game_map=game_map, config=config)
    engine.activate()


if __name__ == '__main__':
    main()