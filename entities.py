"""
Functions that create entities, one for each type of entity.
"""

from bear_hug.bear_utilities import BearECSException
from bear_hug.ecs import Entity, CollisionComponent, WalkerCollisionComponent,\
    WidgetComponent, PositionComponent, PassingComponent,\
    SwitchWidgetComponent, Component, EntityTracker
from bear_hug.event import BearEvent
from bear_hug.widgets import SwitchingWidget

from collections import OrderedDict
from json import dumps, loads


def create_player_tank(dispatcher, atlas):
    player = Entity(id='player')
    player.add_component(InputComponent(dispatcher))
    player.add_component(DestructorHealthComponent(dispatcher, hitpoints=5))
    player.add_component(WalkerCollisionComponent(dispatcher))
    player.add_component(PositionComponent(dispatcher, 10, 10))
    player.add_component(PassingComponent(dispatcher))
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


def create_enemy_tank(dispatcher):
    # ControllerComponent
    # DestructorHealthComponent
    # WalkerCollisionComponent
    # SwitchWidgetComponent
    pass


def create_wall(dispatcher):
    # VisualDamageHealthComponent
    # CollisionComponent
    # PassabilityComponent
    # SwitchWidgetComponent
    pass


def create_bullet(dispatcher):
    # WidgetComponent
    # ProjectileCollisionComponent
    pass

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
                # TODO: shoot
                pass
            elif event.event_value in ('TK_D', 'TK_RIGHT'):
                last_move = (1, 0)
                self.owner.widget.switch_to_image('player_r')
                moved = True
            elif event.event_value in ('TK_A', 'TK_LEFT'):
                last_move = (-1, 0)
                self.owner.widget.switch_to_image('player_l')
                moved = True
            elif event.event_value in ('TK_S', 'TK_DOWN'):
                last_move = (0, 1)
                self.owner.widget.switch_to_image('player_d')
                moved = True
            elif event.event_value in ('TK_W', 'TK_UP'):
                last_move = (0, -1)
                self.owner.widget.switch_to_image('player_u')
                moved = True
            if moved:
                self.owner.position.relative_move(*last_move)
        return r


class ControllerComponent(Component):
    pass


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
            self.owner.destructor.destroy()


class VisualDamageHealthComponent(Component):
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


class ProjectileCollisionComponent(Component):
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