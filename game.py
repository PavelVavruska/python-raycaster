from engine import Engine
from models.player import Player
from models.config import Config
from models.map import Map
from pool import ReusablePool


def main():
    players = ReusablePool(50, Player)

    config = Config(
        fov=80,
        is_perspective_correction_on=True,
        is_metric_on=True,
        pixel_size=1,
        dynamic_lighting=False,
        texture_filtering=True
    )
    game_map = Map()
    engine = Engine(players=players, game_map=game_map, config=config)
    engine.activate()


if __name__ == '__main__':
    main()