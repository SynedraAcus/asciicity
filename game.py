#! /usr/bin/env python3

from bear_hug.bear_hug import BearTerminal, BearLoop
from bear_hug.bear_utilities import copy_shape
from bear_hug.ecs import EntityTracker
from bear_hug.ecs_widgets import ECSLayout
from bear_hug.event import BearEventDispatcher
from bear_hug.resources import Atlas, XpLoader
from bear_hug.sound import SoundListener
from bear_hug.widgets import ClosingListener

################################################################################
# bear_hug boilerplate
################################################################################

# Launching the terminal. All kwargs are bearlibterminal terminal settings
terminal = BearTerminal(font_path='cp437_12x12.png',
                        size='85x60', title='AsciiCity',
                        filter=['keyboard', 'mouse'])
# Setting up the event loop
dispatcher = BearEventDispatcher()
loop = BearLoop(terminal, dispatcher)
# This is used to process window closing
dispatcher.register_listener(ClosingListener(), ['misc_input', 'tick'])
# If not subscribed, EntityTracker won't update its entity list correctly
dispatcher.register_listener(EntityTracker(), ['ecs_create', 'ecs_destroy'])
# Sound system
jukebox = SoundListener({'step': 'dshoof.wav', 'shot': 'dsshotgn.wav'})
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

chars = [['.' for x in range(80)] for y in range(60)]
colors = copy_shape(chars, 'gray')
layout = ECSLayout(chars, colors)
# Subscribing the layout to all events that have 'ecs' as a part of their
# event_type
dispatcher.register_listener(layout, '*ecs')

################################################################################
# Creating game entities
################################################################################

# TODO: entities
# TODO: score Label

################################################################################
# Launching
################################################################################

t.start()
t.add_widget(layout)

loop.run()