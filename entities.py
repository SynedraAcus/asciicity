"""
Functions that create entities, one for each type of entity.
"""

from bear_hug.ecs import CollisionComponent, WidgetComponent


def create_player_tank(dispatcher):
    # InputComponent
    # HealthComponent
    # WalkerCollisionComponent
    # PassabilityComponent
    # SwitchWidgetComponent
    pass


def create_enemy_tank(dispatcher):
    # ControllerComponent
    # HealthComponent
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