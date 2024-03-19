import os
import argparse
import importlib
from ...src.logger import get_logger
from ...src.utils import bool_flag, bcast_json_list
from .utils import get_n_feature_maps
from .game_features import parse_game_features


logger = get_logger()


def parse_game_args(args):
    """
    Parse global game parameters.
    """
    parser = argparse.ArgumentParser(description='Doom parameters')

    # Doom scenario / map ID
    parser.add_argument("--scenario", type=str, default="deathmatch",
                        help="Doom scenario")
    parser.add_argument("--map_id", type=int, default=1,
                        help="Map ID")

    # general game options (freedoom, screen resolution, available buffers,
    # game features, things to render, history size, frame skip, etc)
    parser.add_argument("--freedoom", type=bool_flag, default=True,
                        help="Use freedoom2.wad (as opposed to DOOM2.wad)")
    parser.add_argument("--height", type=int, default=60,
                        help="Image height")
    parser.add_argument("--width", type=int, default=108,
                        help="Image width")
    parser.add_argument("--gray", type=bool_flag, default=False,
                        help="Use grayscale")
    parser.add_argument("--use_screen_buffer", type=bool_flag, default=True,
                        help="Use the screen buffer")
    parser.add_argument("--use_depth_buffer", type=bool_flag, default=False,
                        help="Use the depth buffer")
    parser.add_argument("--labels_mapping", type=str, default='0;1;2;3',
                        help="Map labels to different feature maps")
    parser.add_argument("--game_features", type=str, default='enemy',
                        help="Game features")
    parser.add_argument("--render_hud", type=bool_flag, default=False,
                        help="Render HUD")
    parser.add_argument("--render_crosshair", type=bool_flag, default=True,
                        help="Render crosshair")
    parser.add_argument("--render_weapon", type=bool_flag, default=True,
                        help="Render weapon")
    parser.add_argument("--hist_size", type=int, default=4,
                        help="History size")
    parser.add_argument("--frame_skip", type=int, default=4,
                        help="Number of frames to skip")

    # Available actions
    # combination of actions the agent is allowed to do.
    # this is for non-continuous mode only, and is ignored in continuous mode
    parser.add_argument("--action_combinations", type=str,
                        default='move_fb+turn_lr+move_lr+attack',
                        help="Allowed combinations of actions")
    # freelook: allow the agent to look up and down
    parser.add_argument("--freelook", type=bool_flag, default=False,
                        help="Enable freelook (look up / look down)")
    # speed and crouch buttons: in non-continuous mode, the network can not
    # have control on these buttons, and they must be set to always 'on' or
    # 'off'. In continuous mode, the network can manually control crouch and
    # speed.
    parser.add_argument("--speed", type=str, default='off',
                        help="Crouch: on / off / manual")
    parser.add_argument("--crouch", type=str, default='off',
                        help="Crouch: on / off / manual")

    # number of players / games
    parser.add_argument("--players_per_game", type=int, default=1,
                        help="Number of players per game")
    parser.add_argument("--player_rank", type=int, default=0,
                        help="Player rank")

    # miscellaneous
    parser.add_argument("--dump_path", type=str, default=".",
                        help="Folder to store the models / parameters.")
    parser.add_argument("--visualize", type=bool_flag, default=False,
                        help="Visualize")
    parser.add_argument("--evaluate", type=int, default=0,
                        help="Fast evaluation of the model")
    parser.add_argument("--reload", type=str, default="",
                        help="Reload previous model")
    parser.add_argument("--dump_freq", type=int, default=0,
                        help="Dump every X iterations (0 to disable)")
    parser.add_argument("--gpu_id", type=int, default=0,
                        help="GPU ID")
    parser.add_argument("--log_frequency", type=int, default=100,
                        help="Log frequency (in seconds)")

    # Parse known arguments
    params, _ = parser.parse_known_args(args)

    # check parameters
    assert len(params.dump_path) > 0 and os.path.isdir(params.dump_path)
    assert len(params.scenario) > 0
    assert params.map_id >= 1
    assert params.freelook ^ ('look_ud' not in params.action_combinations)
    assert set([params.speed, params.crouch]).issubset(['on', 'off', 'manual'])
    assert not params.visualize or params.evaluate
    assert not params.evaluate or params.reload
    # assert not params.reload or os.path.isfile(params.reload)

    # run scenario game
    module = importlib.import_module('..scenarios.' + params.scenario,
                                     package=__name__)
    module.main(parser, args)


def finalize_args(params):
    """
    Finalize parameters.
    """
    params.n_variables = len(params.game_variables)
    params.n_features = sum(parse_game_features(params.game_features))
    params.n_fm = get_n_feature_maps(params)

    params.variable_dim = bcast_json_list(params.variable_dim, params.n_variables)
    params.bucket_size = bcast_json_list(params.bucket_size, params.n_variables)

    params.platform = 'doom'
    if not hasattr(params, 'use_continuous'):
        params.use_continuous = False
