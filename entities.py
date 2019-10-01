"""
Functions that create entities, one for each type of entity.
"""

from bear_hug.bear_utilities import BearECSException
from bear_hug.ecs import Entity, CollisionComponent, WalkerCollisionComponent,\
    WidgetComponent, PositionComponent, PassingComponent,\
    SwitchWidgetComponent, Component, EntityTracker, DestructorComponent
from bear_hug.event import BearEvent
from bear_hug.widgets import Widget, SwitchingWidget

from collections import OrderedDict
from json import dumps, loads
from random import choice

################################################################################
# Entity creation functions
################################################################################

# In my real project this would be handled by a dedicated entity factory, which
# takes care of correct entity IDs, loads images from atlas, tracks the
# dispatcher and whatever else may be useful for multiple entities, etc etc.
#
# However, since this is a quick-and-dirty demo with five types of entities,
# a bunch of functions will suffice


def create_player_tank(dispatcher, atlas, x, y):
    # Creating the actual entity, which currently has only a name
    player = Entity(id='player')
    # Adding all necessary components, in our case input (which also spawns
    # bullets), two collision-related ones, position, health and a destructor
    # for orderly entity removal.
    player.add_component(InputComponent(dispatcher))
    player.add_component(WalkerCollisionComponent(dispatcher))
    player.add_component(PassingComponent(dispatcher))
    player.add_component(PositionComponent(dispatcher, x, y))
    player.add_component(DestructorHealthComponent(dispatcher, hitpoints=5))
    player.add_component(DestructorComponent(dispatcher))
    # Also a WidgetComponent, which requires a Widget
    images_dict = {'player_r': atlas.get_element('player_r'),
                   'player_l': atlas.get_element('player_l'),
                   'player_d': atlas.get_element('player_d'),
                   'player_u': atlas.get_element('player_u')}
    player.add_component(SwitchWidgetComponent(dispatcher,
                                               SwitchingWidget(images_dict=images_dict,
                                                               initial_image='player_r')))
    dispatcher.add_event(BearEvent('ecs_create', player))
    dispatcher.add_event(BearEvent('ecs_add', (player.id,
                                               player.position.x,
                                               player.position.y)))
    return player


def create_enemy_tank(dispatcher, atlas, entity_id, x, y):
    # ControllerComponent
    # DestructorHealthComponent
    # WalkerCollisionComponent
    # SwitchWidgetComponent
    enemy = Entity(id=entity_id)
    # Adding all necessary components, in our case input (which also spawns
    # bullets), two collision-related ones, position, health and a destructor
    # for orderly entity removal.
    enemy.add_component(WalkerCollisionComponent(dispatcher))
    enemy.add_component(PassingComponent(dispatcher))
    enemy.add_component(PositionComponent(dispatcher, x, y))
    enemy.add_component(DestructorHealthComponent(dispatcher, hitpoints=1))
    enemy.add_component(DestructorComponent(dispatcher))
    enemy.add_component(ControllerComponent(dispatcher))
    # Also a WidgetComponent, which requires a Widget
    images_dict = {'enemy_r': atlas.get_element('enemy_r'),
                   'enemy_l': atlas.get_element('enemy_l'),
                   'enemy_d': atlas.get_element('enemy_d'),
                   'enemy_u': atlas.get_element('enemy_u')}
    enemy.add_component(SwitchWidgetComponent(dispatcher,
                                               SwitchingWidget(
                                                   images_dict=images_dict,
                                                   initial_image='enemy_r')))
    dispatcher.add_event(BearEvent('ecs_create', enemy))
    dispatcher.add_event(BearEvent('ecs_add', (enemy.id,
                                               enemy.position.x,
                                               enemy.position.y)))
    return enemy


def create_wall(dispatcher, atlas, entity_id, x, y):
    wall = Entity(entity_id)
    wall.add_component(PositionComponent(dispatcher, x, y))
    wall.add_component(VisualDamageHealthComponent(dispatcher,
                                                   hitpoints=3,
                                                   widgets_dict={3: 'wall_3',
                                                                 2: 'wall_2',
                                                                 1: 'wall_1'}))
    wall.add_component(CollisionComponent(dispatcher))
    wall.add_component(DestructorComponent(dispatcher))
    wall.add_component(PassingComponent(dispatcher))
    images_dict = {'wall_3': atlas.get_element('wall_3'),
                   'wall_2': atlas.get_element('wall_2'),
                   'wall_1': atlas.get_element('wall_1')}
    wall.add_component(SwitchWidgetComponent(dispatcher,
                                             SwitchingWidget(images_dict=images_dict,
                                                             initial_image='wall_3')))
    dispatcher.add_event(BearEvent('ecs_create', wall))
    dispatcher.add_event(BearEvent('ecs_add', (wall.id,
                                               wall.position.x,
                                               wall.position.y)))
    pass


def create_bullet(dispatcher, entity_id, x, y, vx, vy):
    bullet = Entity(entity_id)
    bullet.add_component(WidgetComponent(dispatcher,
                                         Widget([['*']], [['red']])))
    bullet.add_component(PositionComponent(dispatcher, x, y,
                                           vx, vy))
    bullet.add_component(ProjectileCollisionComponent(dispatcher, damage=1))
    bullet.add_component(DestructorComponent(dispatcher))
    dispatcher.add_event(BearEvent('ecs_create', bullet))
    dispatcher.add_event(BearEvent('ecs_add', (bullet.id,
                                               bullet.position.x,
                                               bullet.position.y)))
    return bullet


def create_spawner_house(dispatcher, atlas, x, y):
    house = Entity('house')
    house.add_component(WidgetComponent(dispatcher,
                                        Widget(*atlas.get_element('spawner'))))
    house.add_component(DestructorComponent(dispatcher))
    house.add_component(PositionComponent(dispatcher, x, y))
    dispatcher.add_event(BearEvent('ecs_create', house))
    dispatcher.add_event(BearEvent('ecs_add', (house.id,
                                               house.position.x,
                                               house.position.y)))

################################################################################
# Components
################################################################################


class InputComponent(Component):
    """
    A component that handles input.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, name='controller', **kwargs)
        self.dispatcher.register_listener(self, 'key_down')
        self.bullet_count = 0
        self.bullet_offsets = {(1, 0): (7, 2),
                               (-1, 0): (-2, 2),
                               (0, 1): (2, 7),
                               (0, -1): (2, -2)}

    def on_event(self, event):
        x = super().on_event(event)
        if isinstance(x, BearEvent):
            r = [x]
        elif isinstance(x, list):
            r = x
        else:
            r = []
        if event.event_type == 'key_down':
            moved = False
            if event.event_value == 'TK_SPACE':
                bullet_offset = self.bullet_offsets[self.owner.position.last_move]
                create_bullet(self.dispatcher, f'bullet_{self.bullet_count}',
                              self.owner.position.x + bullet_offset[0],
                              self.owner.position.y + bullet_offset[1],
                              self.owner.position.last_move[0] * 20,
                              self.owner.position.last_move[1] * 20)
                self.bullet_count += 1
                self.dispatcher.add_event(BearEvent('play_sound', 'shot'))
            elif event.event_value in ('TK_D', 'TK_RIGHT'):
                move = (1, 0)
                self.owner.widget.switch_to_image('player_r')
                moved = True
            elif event.event_value in ('TK_A', 'TK_LEFT'):
                move = (-1, 0)
                self.owner.widget.switch_to_image('player_l')
                moved = True
            elif event.event_value in ('TK_S', 'TK_DOWN'):
                move = (0, 1)
                self.owner.widget.switch_to_image('player_d')
                moved = True
            elif event.event_value in ('TK_W', 'TK_UP'):
                move = (0, -1)
                self.owner.widget.switch_to_image('player_u')
                moved = True
            if moved:
                # Remembered for shots
                self.direction = move
                self.owner.position.relative_move(*move)
        return r


class ControllerComponent(Component):
    """
    Enemy controller component.

    If has direct line to the player, moves towards him and shoots.
    Otherwise randomly chooses the direction (weighted so that it would be
    mostly towards the player) and keeps moving. If collided into something,
    reconsiders the direction.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dispatcher.register_listener(self, ['tick', 'ecs_collision'])
        # Move 5 steps a second, shoot twice a second
        self.move_delay = 0.1
        self.shoot_delay = 1
        self.move_cd = self.move_delay
        self.shoot_cd = self.shoot_delay
        # Prevents a bug where two tanks collide into each other (eg when one of
        # them spawned on top of another) and infinitely trying to rotate, thus
        # creating more collisions which cause them to try and rotate, and so
        # on and so forth.
        self.rotated_this_tick = False
        self.direction = None
        self.bullet_count = 0
        self.bullet_offsets = {(1, 0): (7, 2),
                               (-1, 0): (-2, 2),
                               (0, 1): (2, 7),
                               (0, -1): (2, -2)}
        self.images = {(1, 0): 'enemy_r',
                       (-1, 0): 'enemy_l',
                       (0, 1): 'enemy_d',
                       (0, -1): 'enemy_u'}

    def on_event(self, event):
        if event.event_type == 'tick':
            self.rotated_this_tick = False
            self.move_cd -= event.event_value
            self.shoot_cd -= event.event_value
            if self.move_cd <= 0:
                try:
                    player_x = EntityTracker().entities['player'].position.x
                    player_y = EntityTracker().entities['player'].position.y
                except KeyError:
                    # DO NOTHING AFTER THE PLAYER IS DEAD
                    return
                dx = player_x - self.owner.position.x
                dy = player_y - self.owner.position.y
                # Turn towards player if has direct line of fire
                if abs(dx) < 3:
                    self.direction = (0, 1 if dy > 0 else -1)
                    self.owner.widget.switch_to_image(
                        self.images[self.direction])
                if abs(dy) < 3:
                    self.direction = (1 if dx > 0 else -1, 0)
                    self.owner.widget.switch_to_image(
                        self.images[self.direction])
                if self.direction is not None:
                    self.owner.position.relative_move(*self.direction)
                    # Shoot if necessary
                    if self.shoot_cd <= 0 and (abs(dx) < 3 or abs(dy) < 3):
                        offset = self.bullet_offsets[self.direction]
                        create_bullet(self.dispatcher,
                                      f'{self.owner.id}_bullet{self.bullet_count}',
                                      self.owner.position.x + offset[0],
                                      self.owner.position.y + offset[1],
                                      self.direction[0] * 20,
                                      self.direction[1] * 20)
                        self.bullet_count += 1
                        self.shoot_cd = self.shoot_delay
                        self.dispatcher.add_event(
                            BearEvent('play_sound', 'shot'))
                else:
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    if dx > 0:
                        directions.extend([(1, 0)] * int(dx / 10))
                    elif dx < 0:
                        directions.extend([(-1, 0)] * int(dx / -10))
                    if dy > 0:
                        directions.extend([(0, 1)] * int(dy / 10))
                    elif dy < 0:
                        directions.extend([(0, -1)] * int(dy / -10))
                    self.direction = choice(directions)
                    self.owner.widget.switch_to_image(self.images[self.direction])
                self.move_cd = self.move_delay
        elif event.event_type == 'ecs_collision'\
                and event.event_value[0] == self.owner.id \
                and not self.rotated_this_tick:
            if event.event_value[1] is None or hasattr(
                                EntityTracker().entities[event.event_value[1]],
                                'collision'):
                self.direction = None
                self.rotated_this_tick = True


class HealthComponent(Component):
    """
    A component that monitors owner's health and updates whatever needs updating

    It waits for the 'ac_damage' events that have event_value set to
    `(entity_id, damage)`. If `entity_id == self.owner`, subtracts damage from
    hitpoints.

    This class should be inherited from, overriding `process_hitpoint_update`
    """

    def __init__(self, *args, hitpoints=3, **kwargs):
        super().__init__(*args, name='health', **kwargs)
        self.dispatcher.register_listener(self, 'ac_damage')
        self._hitpoints = hitpoints

    def on_event(self, event):
        if event.event_type == 'ac_damage' and event.event_value[0] == self.owner.id:
            self.hitpoints -= event.event_value[1]

    @property
    def hitpoints(self):
        return self._hitpoints

    @hitpoints.setter
    def hitpoints(self, value):
        if not isinstance(value, int):
            raise BearECSException(
                f'Attempting to set hitpoints of {self.owner.id} to non-integer {value}')
        self._hitpoints = value
        if self._hitpoints < 0:
            self._hitpoints = 0
        self.process_hitpoint_update()

    def process_hitpoint_update(self):
        """
        Should be overridden by child classes.
        """
        raise NotImplementedError('HP update processing should be overridden')

    def __repr__(self):
        # This game does not actually use serialization (which is meant for
        # saving). Still, it's pretty simple to enable it for your components.
        return dumps({'class': self.__class__.__name__,
                      'hitpoints': self.hitpoints})


class DestructorHealthComponent(HealthComponent):
    """
    Destroys entity upon reaching zero HP
    """
    def process_hitpoint_update(self):
        if self.hitpoints == 0 and hasattr(self.owner, 'destructor'):
            # self.dispatcher.add_event(BearEvent('play_sound', 'explosion'))
            self.dispatcher.add_event(BearEvent('play_sound', 'player_explosion'))
            self.owner.destructor.destroy()



class VisualDamageHealthComponent(HealthComponent):
    """
    A health component for non-active damageable objects.

    Tells the owner's widget to switch image upon reaching certain amounts of HP
    This should be in `widgets_dict` parameter to __init__ which is a dict from
    int HP to image ID. A corresponding image is shown while HP is not less than
    a dict key, but less than the next one (in increasing order).
    If HP reaches zero and object has a Destructor component, it is destroyed
    """

    def __init__(self, *args, widgets_dict={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets_dict = OrderedDict()
        for x in sorted(widgets_dict.keys()):
            # Int conversion useful when loading from JSON, where dict keys get
            # converted to str due to some weird bug. Does nothing during
            # normal Component creation
            self.widgets_dict[int(x)] = widgets_dict[x]

    def process_hitpoint_update(self):
        if self.hitpoints == 0 and hasattr(self.owner, 'destructor'):
            self.owner.destructor.destroy()
        for x in self.widgets_dict:
            if self.hitpoints >= x:
                self.owner.widget.switch_to_image(self.widgets_dict[x])

    def __repr__(self):
        d = loads(super().__repr__())
        d['widgets_dict'] = self.widgets_dict
        return dumps(d)


class ProjectileCollisionComponent(CollisionComponent):
    """
    A collision component that damages whatever its owner is collided into
    """

    def __init__(self, *args, damage=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.damage = damage

    def collided_into(self, entity):
        if not entity:
            self.owner.destructor.destroy()
        elif hasattr(EntityTracker().entities[entity], 'collision'):
            self.dispatcher.add_event(BearEvent(event_type='ac_damage',
                                                event_value=(
                                                entity, self.damage)))
            self.owner.destructor.destroy()

    def __repr__(self):
        d = loads(super().__repr__())
        d['damage'] = self.damage
        return dumps(d)