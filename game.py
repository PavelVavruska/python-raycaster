from engine import Engine
from models.player import Player
from models.config import Config
from models.map import Map


def main():
    players = []
    for number in range(4):
        player = Player(2, 3+number, 10*number)
        players.append(player)

    config = Config(
        fov=100,
        is_perspective_correction_on=True,
        is_metric_on=True,
        pixel_size=2,
        dynamic_lighting=False,
        texture_filtering=True
    )
    game_map = Map()
    engine = Engine(players=players, game_map=game_map, config=config)
    engine.activate()


if __name__ == '__main__':
    main()