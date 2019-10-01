"""
A few listeners/widgets
"""

from bear_hug.widgets import Label, Listener
from entities import create_enemy_tank


class ScoreLabel(Label):
    """
    Scores for the destroyed enemy tanks
    """
    def __init__(self, *args, **kwargs):
        super().__init__(text='Score:\n0')
        self.score = 0

    def on_event(self, event):
        if event.event_type == 'ecs_destroy' and 'enemy' in event.event_value and 'bullet' not in event.event_value:
            self.score += 10
            self.text = f'Score:\n{self.score}'
            self.terminal.update_widget(self)


class HPLabel(Label):
    """
    Player HP
    """
    def __init__(self, *args, **kwargs):
        super().__init__(text='HP:\n5')
        self.hp = 5

    def on_event(self, event):
        if event.event_type == 'ac_damage' and event.event_value[0] == 'player':
            self.hp -= event.event_value[1]
            self.text = f'HP:\n{self.hp}'
            self.terminal.update_widget(self)


class SpawnerListener(Listener):
    """
    Spawns enemy tanks on cooldown, until there are enough of them
    """
    def __init__(self, *args, dispatcher, atlas, x, y,
                 cooldown=2.0, enemies=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldown = cooldown
        # Set to zero to spawn first enemy immediately
        self.spawn_cd = 0
        self.enemies = enemies
        self.enemies_current = 0
        # Another counter for enemies. This one is used for IDs and never
        # decrements
        self.counter = 0
        # Store all data for enemy creation
        self.dispatcher = dispatcher
        self.atlas = atlas
        self.x = x
        self.y = y

    def on_event(self, event):
        if event.event_type == 'ecs_destroy' and 'enemy' in event.event_value:
            self.enemies_current -= 1
        if event.event_type == 'tick':
            self.spawn_cd -= event.event_value
            if self.spawn_cd <= 0 and self.enemies_current < self.enemies:
                create_enemy_tank(self.dispatcher, self.atlas,
                                  f'enemy_{self.counter}',
                                  self.x, self.y)
                self.spawn_cd = self.cooldown
                self.enemies_current += 1
                self.counter += 1