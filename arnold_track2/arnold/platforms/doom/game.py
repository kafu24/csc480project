from __future__ import print_function  # for DOOM
import os
import time
from collections import namedtuple

# ViZDoom library
from vizdoom import DoomGame, GameVariable
from vizdoom import ScreenResolution, ScreenFormat, Mode

# Arnold
# from . import RESOURCES_DIR, VIZDOOM_PATH
from ...src.logger import get_logger
from .utils import process_buffers
from .actions import add_buttons
from .game_features import parse_game_features

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources')

WEAPON_NAMES = [None, "Fist", "Pistol", "SuperShotgun", "Chaingun",
                "RocketLauncher", "PlasmaRifle", "BFG9000"]

WEAPONS_PREFERENCES = [
    ('bfg9000', 'cells', 7), ('shotgun', 'shells', 3),
    ('chaingun', 'bullets', 4), ('plasmarifle', 'cells', 6),
    ('pistol', 'bullets', 2), ('rocketlauncher', 'rockets', 5)
]

RESPAWN_SECONDS = 10

# game variables we want to use
game_variables = [
    # ('KILLCOUNT', GameVariable.KILLCOUNT),
    # ('ITEMCOUNT', GameVariable.ITEMCOUNT),
    # ('SECRETCOUNT', GameVariable.SECRETCOUNT),
    ('frag_count', GameVariable.FRAGCOUNT),
    # ('DEATHCOUNT', GameVariable.DEATHCOUNT),
    ('health', GameVariable.HEALTH),
    ('armor', GameVariable.ARMOR),
    # ('DEAD', GameVariable.DEAD),
    # ('ON_GROUND', GameVariable.ON_GROUND),
    # ('ATTACK_READY', GameVariable.ATTACK_READY),
    # ('ALTATTACK_READY', GameVariable.ALTATTACK_READY),
    ('sel_weapon', GameVariable.SELECTED_WEAPON),
    ('sel_ammo', GameVariable.SELECTED_WEAPON_AMMO),
    # ('AMMO0', GameVariable.AMMO0),  # UNK
    # ('AMMO1', GameVariable.AMMO1),  # fist weapon, should always be 0
    ('bullets', GameVariable.AMMO2),  # bullets
    ('shells', GameVariable.AMMO3),  # shells
    # ('AMMO4', GameVariable.AMMO4),  # == AMMO2
    ('rockets', GameVariable.AMMO5),  # rockets
    ('cells', GameVariable.AMMO6),  # cells
    # ('AMMO7', GameVariable.AMMO7),  # == AMMO6
    # ('AMMO8', GameVariable.AMMO8),  # UNK
    # ('AMMO9', GameVariable.AMMO9),  # UNK
    # ('WEAPON0', GameVariable.WEAPON0),  # UNK
    ('fist', GameVariable.WEAPON1),  # Fist, should be 1, unless removed
    ('pistol', GameVariable.WEAPON2),  # Pistol
    ('shotgun', GameVariable.WEAPON3),  # Shotgun
    ('chaingun', GameVariable.WEAPON4),  # Chaingun
    ('rocketlauncher', GameVariable.WEAPON5),  # Rocket Launcher
    ('plasmarifle', GameVariable.WEAPON6),  # Plasma Rifle
    ('bfg9000', GameVariable.WEAPON7),  # BFG9000
    # ('WEAPON8', GameVariable.WEAPON8),  # UNK
    # ('WEAPON9', GameVariable.WEAPON9),  # UNK
]

# advance a few steps to avoid bugs due to initial weapon changes
SKIP_INITIAL_ACTIONS = 3


# game state
GameState = namedtuple('State', ['screen', 'variables', 'features'])

# logger
logger = get_logger()


class Game(object):

    def __init__(
        self,
        scenario,
        action_builder,
        reward_values=None,
        score_variable='FRAGCOUNT',
        freedoom=True,
        screen_resolution='RES_400X225',
        screen_format='CRCGCB',
        use_screen_buffer=True,
        use_depth_buffer=False,
        labels_mapping='',
        game_features='',
        mode='PLAYER',
        player_rank=0, players_per_game=1,
        render_hud=False, render_minimal_hud=False,
        render_crosshair=True, render_weapon=True,
        render_decals=False,
        render_particles=False,
        render_effects_sprites=False,
        respawn_protect=True, spawn_farthest=True,
        freelook=False, name='no_name', color=1,
        visible=False,
        n_bots=0, use_scripted_marines=None,
        doom_skill=2
    ):
        """
        Create a new game.
        score_variable: indicates in which game variable the user score is
            stored. by default it's in FRAGCOUNT, but the score in ACS against
            built-in AI bots can be stored in USER1, USER2, etc.
        render_decals: marks on the walls
        render_particles: particles like for impacts / traces
        render_effects_sprites: gun puffs / blood splats
        color: 0 - green, 1 - gray, 2 - brown, 3 - red, 4 - light gray,
               5 - light brown, 6 - light red, 7 - light blue
        """
        # game resources
        game_filename = '%s.wad' % ('freedoom2' if freedoom else 'Doom2')
        self.scenario_path = os.path.join(RESOURCES_DIR, 'scenarios',
                                          '%s.wad' % scenario)
        self.game_path = os.path.join(RESOURCES_DIR, game_filename)
        # self.scenario_path = '/home/sbcmkiii/ViZDoom/scenarios/dwango5.wad'
        # self.game_path = '/home/sbcmkiii/CalPoly/csc480/freedoom2.wad'

        # check parameters
        print(scenario)
        print(self.scenario_path)
        assert os.path.isfile(self.scenario_path)
        assert os.path.isfile(self.game_path)
        assert hasattr(GameVariable, score_variable)
        assert hasattr(ScreenResolution, screen_resolution)
        assert hasattr(ScreenFormat, screen_format)
        assert use_screen_buffer or use_depth_buffer
        assert hasattr(Mode, mode)
        assert not (render_minimal_hud and not render_hud)
        assert len(name.strip()) > 0 and color in range(8)
        assert n_bots >= 0
        assert (type(use_scripted_marines) is bool or
                use_scripted_marines is None and n_bots == 0)
        assert 0 <= doom_skill <= 4
        assert 0 < players_per_game
        assert 0 <= player_rank

        # action builder
        self.action_builder = action_builder

        # add the score variable to the game variables list
        self.score_variable = score_variable
        game_variables.append(('score', getattr(GameVariable, score_variable)))

        self.player_rank = player_rank
        self.players_per_game = players_per_game

        # screen buffer / depth buffer / labels buffer / mode
        self.screen_resolution = screen_resolution
        self.screen_format = screen_format
        self.use_screen_buffer = use_screen_buffer
        self.use_depth_buffer = use_depth_buffer
        self.labels_mapping = None
        self.game_features = parse_game_features(game_features)
        self.use_labels_buffer = self.labels_mapping is not None
        self.use_game_features = any(self.game_features)
        self.mode = mode

        # rendering options
        self.render_hud = render_hud
        self.render_minimal_hud = render_minimal_hud
        self.render_crosshair = render_crosshair
        self.render_weapon = render_weapon
        self.render_decals = render_decals
        self.render_particles = render_particles
        self.render_effects_sprites = render_effects_sprites

        # respawn invincibility / distance
        self.respawn_protect = respawn_protect
        self.spawn_farthest = spawn_farthest

        # freelook / agent name / agent color
        self.freelook = freelook
        self.name = name.strip()
        self.color = color

        # window visibility
        self.visible = visible

        # game statistics
        self.stat_keys = ['kills', 'deaths', 'suicides', 'frags', 'k/d',
                          'medikits', 'armors',
                          'pistol', 'shotgun', 'chaingun',
                          'rocketlauncher', 'plasmarifle', 'bfg9000',
                          'bullets', 'shells', 'rockets', 'cells']
        self.statistics = {}

        # number of bots in the game
        self.n_bots = n_bots
        self.use_scripted_marines = use_scripted_marines

        # doom skill
        self.doom_skill = doom_skill

        # manual control
        self.count_non_forward_actions = 0
        self.count_non_turn_actions = 0

    def update_game_variables(self):
        """Check and update game variables."""
        # read game variables
        new_v = {k: self.game.get_game_variable(v) for k, v in game_variables}
        assert all(v.is_integer() or k[-2:] in ['_x', '_y', '_z'] for k, v in new_v.items())
        new_v = {k: (int(v) if v.is_integer() else float(v)) for k, v in new_v.items()}
        health = new_v['health']
        armor = new_v['armor']
        sel_weapon = new_v['sel_weapon']
        sel_ammo = new_v['sel_ammo']
        bullets = new_v['bullets']
        shells = new_v['shells']
        rockets = new_v['rockets']
        cells = new_v['cells']
        fist = new_v['fist']
        pistol = new_v['pistol']
        shotgun = new_v['shotgun']
        chaingun = new_v['chaingun']
        rocketlauncher = new_v['rocketlauncher']
        plasmarifle = new_v['plasmarifle']
        bfg9000 = new_v['bfg9000']

        # check game variables
        if sel_weapon == -1:
            logger.warning("SELECTED WEAPON is -1!")
            new_v['sel_weapon'] = 1
            sel_weapon = 1
        if sel_ammo == -1:
            logger.warning("SELECTED AMMO is -1!")
            new_v['sel_ammo'] = 0
            sel_ammo = 0
        assert sel_weapon in range(1, 8), sel_weapon
        assert sel_ammo >= 0, sel_ammo
        assert all(x in [0, 1, 2] for x in [fist, pistol, shotgun, chaingun,
                                            rocketlauncher, plasmarifle, bfg9000])
        assert 0 <= health <= 200 or health < 0 and self.game.is_player_dead()
        assert 0 <= armor <= 200, (health, armor)
        assert 0 <= bullets <= 200 and 0 <= shells <= 50
        assert 0 <= rockets <= 50 and 0 <= cells <= 300

        # fist
        if sel_weapon == 1:
            assert sel_ammo == 0
        # pistol
        elif sel_weapon == 2:
            assert pistol and sel_ammo == bullets
        # shotgun
        elif sel_weapon == 3:
            assert shotgun and sel_ammo == shells
        # chaingun
        elif sel_weapon == 4:
            assert chaingun and sel_ammo == bullets
        # rocket launcher
        elif sel_weapon == 5:
            assert rocketlauncher and sel_ammo == rockets
        # plasma rifle
        elif sel_weapon == 6:
            assert plasmarifle and sel_ammo == cells
        # BFG9000
        elif sel_weapon == 7:
            assert bfg9000 and sel_ammo == cells

        # update actor properties
        self.prev_properties = self.properties
        self.properties = new_v

    def start(self, map_id, episode_time=None):
        """
        Start the game.
        If `episode_time` is given, the game will end after the specified time.
        """
        # Save statistics for this map
        self.statistics[map_id] = {k: 0 for k in self.stat_keys}

        # Episode time
        self.episode_time = episode_time

        # initialize the game
        self.game = DoomGame()
        # self.game.set_vizdoom_path(VIZDOOM_PATH)
        self.game.set_doom_scenario_path(self.scenario_path)
        self.game.set_doom_game_path(self.game_path)

        # map
        assert map_id > 0
        self.map_id = map_id
        self.game.set_doom_map("map%02i" % map_id)

        # time limit
        # if episode_time is not None:
        #     self.game.set_episode_timeout(int(35 * episode_time))

        # game parameters
        args = []

        # host / server
        # args.append('-join localhost')

        # screen buffer / depth buffer / labels buffer / mode
        screen_resolution = ScreenResolution.names[self.screen_resolution]
        self.game.set_screen_resolution(screen_resolution)
        self.game.set_screen_format(ScreenFormat.names[self.screen_format])
        self.game.set_depth_buffer_enabled(self.use_depth_buffer)
        self.game.set_labels_buffer_enabled(self.use_labels_buffer or
                                            self.use_game_features)
        # self.game.set_mode(Mode.names[self.mode])

        # rendering options
        self.game.set_render_hud(self.render_hud)
        self.game.set_render_minimal_hud(self.render_minimal_hud)
        self.game.set_render_crosshair(self.render_crosshair)
        self.game.set_render_weapon(self.render_weapon)
        self.game.set_render_decals(self.render_decals)
        self.game.set_render_particles(self.render_particles)
        self.game.set_render_effects_sprites(self.render_effects_sprites)

        # deathmatch mode
        # players will respawn automatically after they die
        # autoaim is disabled for all players
        args.append('-deathmatch')
        # args.append('+sv_forcerespawn 1')
        # args.append('+sv_noautoaim 1')

        # respawn invincibility / distance
        # players will be invulnerable for two second after spawning
        # players will be spawned as far as possible from any other players
        # args.append('+sv_respawnprotect %i' % self.respawn_protect)
        # args.append('+sv_spawnfarthest %i' % self.spawn_farthest)

        # freelook / agent name / agent color
        args.append('+freelook %i' % (1 if self.freelook else 0))
        args.append('+name %s' % self.name)
        args.append('+colorset %i' % self.color)

        # enable the cheat system (so that we can still
        # send commands to the game in self-play mode)
        # args.append('+sv_cheats 1')

        # load parameters
        self.args = args
        for arg in args:
            self.game.add_game_args(arg)

        # window visibility
        self.game.set_window_visible(self.visible)

        # available buttons
        self.mapping = add_buttons(self.game, self.action_builder.available_buttons)

        # doom skill (https://zdoom.org/wiki/GameSkill)
        # self.game.set_doom_skill(self.doom_skill + 1)

        # start the game
        self.game.init()

        # initialize the game after player spawns
        self.initialize_game()

    def reset(self):
        """
        Reset the game if necessary. This can be because:
            - we reach the end of an episode (we restart the game)
            - because the agent is dead (we make it respawn)
        """
        self.count_non_forward_actions = 0
        self.count_non_turn_actions = 0
        # if the player is dead
        if self.is_player_dead():
            # respawn it (deathmatch mode)
            if self.episode_time is None:
                self.respawn_player()
            # or reset the episode (episode ends when the agent dies)
            else:
                self.new_episode()

        # start a new episode if it is finished
        if self.is_episode_finished():
            self.new_episode()

        # deal with a ViZDoom issue
        while self.is_player_dead():
            logger.warning('Player %i is still dead after respawn.' %
                           self.params.player_rank)
            self.respawn_player()

    def update_bots(self):
        """
        Add built-in AI bots.
        There are two types of AI: built-in AI and ScriptedMarines.
        """
        return
        # only the host takes care of the bots
        if self.player_rank % self.players_per_game != 0:
            return
        if self.use_scripted_marines:
            command = "pukename set_value always 2 %i" % self.n_bots
            self.game.send_game_command(command)
        else:
            self.game.send_game_command("removebots")
            for _ in range(self.n_bots):
                self.game.send_game_command("addbot")

    def is_player_dead(self):
        """Detect whether the player is dead."""
        return self.game.is_player_dead()

    def is_episode_finished(self):
        """
        Return whether the episode is finished.
        This should only be the case after the episode timeout.
        """
        return self.game.is_episode_finished()

    def is_final(self):
        """Return whether the game is in a final state."""
        return self.is_player_dead() or self.is_episode_finished()

    def new_episode(self):
        """Start a new episode."""
        assert self.is_episode_finished() or self.is_player_dead()
        self.game.new_episode()
        self.initialize_game()

    def respawn_player(self):
        """Respawn the player on death."""
        assert self.is_player_dead()
        self.game.respawn_player()
        self.initialize_game()

    def initialize_game(self):
        """
        Initialize the game after the player spawns / respawns.
        Be sure that properties from the previous
        life are not considered in this one.
        """
        # generate buffers
        game_state = self.game.get_state()
        self._screen_buffer = game_state.screen_buffer
        self._depth_buffer = game_state.depth_buffer
        self._labels_buffer = game_state.labels_buffer
        self._labels = game_state.labels

        # actor properties
        self.prev_properties = None
        self.properties = None

        # advance a few steps to avoid bugs due
        # to initial weapon changes in ACS
        self.game.advance_action(SKIP_INITIAL_ACTIONS)
        self.update_game_variables()

        # if there are bots in the game, and if this is a new game
        self.update_bots()

    def make_action(self, action, frame_skip=1, sleep=None):
        """
        Make an action.
        If `sleep` is given, the network will wait
        `sleep` seconds between each action.
        """
        assert frame_skip >= 1

        # convert selected action to the ViZDoom action format
        action = self.action_builder.get_action(action)

        # select agent favorite weapon
        for weapon_name, weapon_ammo, weapon_id in WEAPONS_PREFERENCES:
            min_ammo = 40 if weapon_name == 'bfg9000' else 1
            if self.properties[weapon_name] > 0 and self.properties[weapon_ammo] >= min_ammo:
                if self.properties['sel_weapon'] != weapon_id:
                    # action = ([False] * self.mapping['SELECT_WEAPON%i' % weapon_id]) + [True]
                    switch_action = ([False] * self.mapping['SELECT_WEAPON%i' % weapon_id]) + [True]
                    action = action + switch_action[len(action):]
                    print("Manual weapon change: %s -> %s" % (WEAPON_NAMES[self.properties['sel_weapon']], weapon_name))
                break

        if action[self.mapping['MOVE_FORWARD']]:
            self.count_non_forward_actions = 0
        else:
            self.count_non_forward_actions += 1

        if action[self.mapping['TURN_LEFT']] or action[self.mapping['TURN_RIGHT']]:
            self.count_non_turn_actions = 0
        else:
            self.count_non_turn_actions += 1

        if self.count_non_forward_actions >= 30 or self.count_non_turn_actions >= 60:
            if self.count_non_forward_actions >= 30:
                print("Manual control (non forward)")
            if self.count_non_turn_actions >= 60:
                print("Manual control (non turn)")
            manual_action = [False] * len(action)
            manual_action[self.mapping['TURN_RIGHT']] = True
            manual_action[self.mapping['SPEED']] = True
            if self.count_non_forward_actions >= 30:
                manual_action[self.mapping['MOVE_FORWARD']] = True
            manual_repeat = 40
            self.count_non_forward_actions = 0
            self.count_non_turn_actions = 0
        else:
            manual_action = None

        # if we are visualizing the experiment, show all the frames one by one
        if self.visible:
            if manual_action is not None:
                logger.warning('Activated manual control')
                for _ in range(manual_repeat):
                    self.game.make_action(manual_action)
            else:
                for _ in range(frame_skip):
                    self.game.make_action(action)
                    # death or episode finished
                    if self.is_player_dead() or self.is_episode_finished():
                        break
                    # sleep for smooth visualization
                    if sleep is not None:
                        time.sleep(sleep)
        else:
            if manual_action is not None:
                logger.warning('Activated manual control')
                self.game.make_action(manual_action, manual_repeat)
            else:
                self.game.make_action(action, frame_skip)

        # generate buffers
        game_state = self.game.get_state()
        self._screen_buffer = game_state.screen_buffer
        self._depth_buffer = game_state.depth_buffer
        self._labels_buffer = game_state.labels_buffer
        self._labels = game_state.labels

        # update game variables / statistics rewards
        self.update_game_variables()

    def close(self):
        """Close the current game."""
        self.game.close()

    def observe_state(self, params, last_states):
        """
        Observe the current state of the game.
        """
        # read game state
        screen, game_features = process_buffers(self, params)
        variables = [self.properties[x[0]] for x in params.game_variables]
        last_states.append(GameState(screen, variables, game_features))

        # update most recent states
        if len(last_states) == 1:
            last_states.extend([last_states[0]] * (params.hist_size - 1))
        else:
            assert len(last_states) == params.hist_size + 1
            del last_states[0]

        # return the screen and the game features
        return screen, game_features

