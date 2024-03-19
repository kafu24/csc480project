from __future__ import print_function  # for DOOM
import os
import torch
import pickle
import timeit

# Arnold
from ....src.utils import set_num_threads, get_device_mapping
from ....src.logger import get_logger
from ....src.model import register_model_args, get_model_class
from ..args import finalize_args
from ..game import Game
from ..actions import ActionBuilder


logger = get_logger()


def register_scenario_args(parser):
    # register scenario parameters
    parser.add_argument("--n_bots", type=int, default=8,
                        help="Number of ACS bots in the game")
    parser.add_argument("--wad", type=str, default="",
                        help="WAD scenario filename")


def main(parser, args, parameter_server=None):

    # register model and scenario parameters / parse parameters
    register_model_args(parser, args)
    register_scenario_args(parser)
    params = parser.parse_args(args)

    # Game variables / Game features / feature maps
    params.game_variables = [('health', 101), ('sel_ammo', 301)]
    finalize_args(params)

    # Training / Evaluation parameters
    params.episode_time = None  # episode maximum duration (in seconds)

    # log experiment parameters
    with open(os.path.join(params.dump_path, 'params.pkl'), 'wb') as f:
        pickle.dump(params, f)
    logger.info('\n'.join('%s: %s' % (k, str(v))
                          for k, v in dict(vars(params)).items()))

    # use only 1 CPU thread / set GPU ID if required
    set_num_threads(1)
    if params.gpu_id >= 0:
        torch.cuda.set_device(params.gpu_id)

    # Action builder
    action_builder = ActionBuilder(params)

    # Initialize the game
    game = Game(
        scenario=params.wad,
        action_builder=action_builder,
        score_variable='USER2',
        freedoom=params.freedoom,
        # screen_resolution='RES_400X225',
        use_screen_buffer=params.use_screen_buffer,
        use_depth_buffer=params.use_depth_buffer,
        labels_mapping=params.labels_mapping,
        game_features=params.game_features,
        mode='PLAYER',
        player_rank=params.player_rank,
        players_per_game=params.players_per_game,
        render_hud=params.render_hud,
        render_crosshair=params.render_crosshair,
        render_weapon=params.render_weapon,
        freelook=params.freelook,
        visible=params.visualize,
        n_bots=0,
        use_scripted_marines=True,
        name='Arnold4'
    )

    # Network initialization and optional reloading
    network = get_model_class(params.network_type)(params)
    if params.reload:
        logger.info('Reloading model from %s...' % params.reload)
        model_path = os.path.join(params.dump_path, params.reload)
        map_location = get_device_mapping(params.gpu_id)
        network.module = torch.load(model_path, map_location=map_location)
    assert params.n_features == network.module.n_features

    logger.info('Evaluating the model...')
    game.start(map_id=params.map_id)
    network.reset()
    network.module.eval()

    n_iter = 0
    last_states = []

    count_actions = 0
    start_time = timeit.default_timer()

    while True:
        n_iter += 1

        if game.is_player_dead():
            game.respawn_player()
            network.reset()

        while game.is_player_dead():
            logger.warning('Player %i is still dead after respawn.' %
                           params.player_rank)
            game.respawn_player()

        # observe the game state / select the next action
        game.observe_state(params, last_states)
        action = network.next_action(last_states)

    count_actions += 1
    if count_actions%100 == 0:
        elapsed = timeit.default_timer() - start_time
        start_time = timeit.default_timer()
        print(elapsed)
        
    sleep = 0 if params.evaluate else None  # TOCHECK for eval
    game.make_action(action, params.frame_skip, sleep=sleep)

    # close the game
    game.close()
