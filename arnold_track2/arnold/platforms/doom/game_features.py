from ...src.logger import get_logger


# logger
logger = get_logger()


def parse_game_features(s):
    """
    Parse the game features we want to detect.
    """
    game_features = ['target', 'enemy', 'health', 'weapon', 'ammo']
    split = list(filter(None, s.split(',')))
    assert all(x in game_features for x in split)
    return [x in split for x in game_features]
