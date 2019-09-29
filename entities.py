"""
Functions that create entities, one for each type of entity.
"""

from bear_hug.ecs import Entity, CollisionComponent, WalkerCollisionComponent,\
    WidgetComponent, PositionComponent, PassingComponent, SwitchWidgetComponent
from bear_hug.widgets import SwitchingWidget

from components import *


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