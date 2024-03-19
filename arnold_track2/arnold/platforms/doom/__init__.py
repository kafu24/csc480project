import sys
import os
from .args import parse_game_args


# ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..')
# RESOURCES_DIR = os.path.join(ROOT_DIR, 'resources')
# LIB_DIR = os.path.join(ROOT_DIR, 'lib')
# LIB_DIR = '/'
# # VIZDOOM_BIN_DIR = os.path.join(LIB_DIR, 'ViZDoom', 'bin')


# assert os.path.isdir(RESOURCES_DIR)
# assert os.path.isdir(LIB_DIR)
# assert os.path.isdir(VIZDOOM_BIN_DIR)

# VIZDOOM_BIN_DIR = os.path.join(LIB_DIR, 'ViZDoom', 'bin')
# if sys.platform == 'darwin':
#     VIZDOOM_PATH = os.path.join(VIZDOOM_BIN_DIR, 'vizdoom.app', 'Contents',
#                                 'MacOS', 'vizdoom')
# else:
#     VIZDOOM_PATH = os.path.join(VIZDOOM_BIN_DIR, 'vizdoom')

# assert os.path.isdir(VIZDOOM_BIN_DIR), VIZDOOM_BIN_DIR
# assert os.path.isfile(VIZDOOM_PATH), VIZDOOM_PATH

# sys.path.append(os.path.join(VIZDOOM_BIN_DIR, 'python2'))
# sys.path.append(os.path.join(VIZDOOM_BIN_DIR, 'python3'))


def main(args):
    parse_game_args(args)
