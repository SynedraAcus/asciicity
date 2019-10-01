#! /usr/bin/env python3

from bear_hug.bear_hug import BearTerminal, BearLoop
from bear_hug.bear_utilities import copy_shape
from bear_hug.ecs import EntityTracker
from bear_hug.ecs_widgets import ECSLayout
from bear_hug.event import BearEventDispatcher
from bear_hug.resources import Atlas, XpLoader
from bear_hug.sound import SoundListener
from bear_hug.widgets import Widget, ClosingListener, LoggingListener

import sys

from entities import *
from listeners import *

################################################################################
# bear_hug boilerplate
################################################################################

# Launching the terminal. All kwargs are bearlibterminal terminal settings
terminal = BearTerminal(font_path='cp437_12x12.png',
                        size='91x60', title='AsciiCity',
                        filter=['keyboard', 'mouse'])
# Setting up the event loop
dispatcher = BearEventDispatcher()
loop = BearLoop(terminal, dispatcher)
# This is used to process window closing
dispatcher.register_listener(ClosingListener(), ['misc_input', 'tick'])
# If not subscribed, EntityTracker won't update its entity list correctly
dispatcher.register_listener(EntityTracker(), ['ecs_create', 'ecs_destroy'])
# Sound system
jukebox = SoundListener({})
dispatcher.register_listener(jukebox, 'play_sound')


################################################################################
# loading game data
################################################################################

# Loading image atlas
atlas = Atlas(XpLoader('battlecity.xp'),
              'battlecity.json')
# TODO: add sounds

################################################################################
# Layout
################################################################################

# Setting the level layout and its background.
# Note that it's 80x60, while the window is 85x60. Rightmost 5 columns will be
# used for score.

chars = [[' ' for x in range(84)] for y in range(60)]
colors = copy_shape(chars, 'gray')
layout = ECSLayout(chars, colors)
# Subscribing the layout to all events that have 'ecs' as a part of their
# event_type
dispatcher.register_listener(layout, 'all')

################################################################################
# Creating game-specific entities and events
################################################################################

# Damage event type. Value set to (entity_id, damage)
# This event type is prefixed with 'ac' (for AsciiCity) to separate it from
# other event types
dispatcher.register_event_type('ac_damage')
# Setting up logging for this kind of event, just in case
logger = LoggingListener(sys.stderr)
dispatcher.register_listener(logger, 'ecs_create')

# Creating in-game entities
create_player_tank(dispatcher, atlas, 30, 50)
create_wall(dispatcher, atlas, 'wall', 20, 20)
wall_array = [[0 for _ in range(14)],
              [0 for _ in range(14)],
              [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
              [1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
              [1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1],
              [1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0],
              [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0],
              [0 for _ in range(14)],
              [0 for _ in range(14)],
              [0 for _ in range(14)]
              ]
for y in range(10):
    for x in range(14):
        if wall_array[y][x] == 1:
            create_wall(dispatcher, atlas, f'wall{x}{y}', x*6, y*6)
# Spawner house is just an image. It doesn't even collide.
create_spawner_house(dispatcher, atlas, 35, 0)
# Actual spawning is done by this invisible listener:
spawner = SpawnerListener(dispatcher=dispatcher,
                          atlas=atlas,
                          x=36, y=1,
                          cooldown=5.0,
                          enemies=3)
dispatcher.register_listener(spawner, ['tick', 'ecs_destroy'])
# These two are sidebar widgets, which can accept the events but are outside the
# ECSLayout (ie game map)
score = ScoreLabel(terminal)
dispatcher.register_listener(score, 'ecs_destroy')
hp = HPLabel(terminal)
dispatcher.register_listener(hp, 'ac_damage')
# And this listener should display the GAME OVER widget
gameover_widget = Widget(*atlas.get_element('game_over'))
gameover_listener = GameOverListener(terminal, widget=gameover_widget)
dispatcher.register_listener(gameover_listener, 'ecs_destroy')

################################################################################
# Launching
################################################################################

terminal.start()
terminal.add_widget(layout)
terminal.add_widget(score, pos=(85, 10))
terminal.add_widget(hp, pos=(85, 15))
loop.run()