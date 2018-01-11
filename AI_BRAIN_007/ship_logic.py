from collections import OrderedDict
from enum import Enum


import hlt
import logging
from AI_BRAIN_007 import ship_control


class EnemyCloseness(Enum):
    NEARBY = 0
    ON_RADAR = 1
    FAR_AWAY = 2

enemy_nearby = {
    hlt.entity.Ship.Role.SETTLE: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.START: lambda s, gm, ce, cp, pp: ship_control.move(s, cp, gm),
    hlt.entity.Ship.Role.DOCK: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.ATTACK: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.DEFEND: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.DISTRACT: lambda s, gm, ce, cp, pp: ship_control.retreat(s, ce),
}

enemy_on_radar = {
    hlt.entity.Ship.Role.SETTLE: lambda s, gm, ce, cp, pp: settle(s, pp, gm),
    hlt.entity.Ship.Role.START: lambda s, gm, ce, cp, pp: ship_control.move(s, cp, gm),
    hlt.entity.Ship.Role.DOCK: lambda s, gm, ce, cp, pp: ship_control.move(s, cp, gm),
    hlt.entity.Ship.Role.ATTACK: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.DEFEND: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.DISTRACT: lambda s, gm, ce, cp, pp: ship_control.investigate(s, ce),
}

enemy_far_away = {
    hlt.entity.Ship.Role.SETTLE: lambda s, gm, ce, cp, pp: settle(s, pp, gm),
    hlt.entity.Ship.Role.START: lambda s, gm, ce, cp, pp: ship_control.move(s, cp, gm),
    hlt.entity.Ship.Role.DOCK: lambda s, gm, ce, cp, pp: ship_control.move(s, cp, gm),
    hlt.entity.Ship.Role.ATTACK: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
    hlt.entity.Ship.Role.DEFEND: lambda s, gm, ce, cp, pp: ship_control.destroy(s, cp, gm),
    hlt.entity.Ship.Role.DISTRACT: lambda s, gm, ce, cp, pp: ship_control.destroy(s, ce, gm),
}

#################################################
#  Decides which dictionary to get values from  #
#################################################

perform_ship_action = {
    EnemyCloseness.NEARBY: lambda s, gm, ce, cp, pp: enemy_nearby[s.role](s, gm, ce, cp, pp),
    EnemyCloseness.ON_RADAR: lambda s, gm, ce, cp, pp: enemy_on_radar[s.role](s, gm, ce, cp, pp),
    EnemyCloseness.FAR_AWAY: lambda s, gm, ce, cp, pp: enemy_far_away[s.role](s, gm, ce, cp, pp),
}

#################################################


def get_closest_enemy(ship, game_map):
    """
    Find the closest enemy to the ship
    :param ship: current ship being controlled
    :param game_map: the map of the game
    :return: Ship object for the nearest enemy
    """
    # Collect information about all entities near the ship
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

    # Get all enemy ships
    enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance
                   if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                   not entities_by_distance[distance][0] in game_map.get_me().all_ships()]

    return enemy_ships[0]


def settle(ship, planned_planets, game_map):
    """
    Moves the ship towards the empty planet
    :param ship: current ship being controlled
    :param planned_planets: list of empty planets being traveled to
    :param game_map: the map of the game
    :return: action to be entered into command_queue
    """
    # Collect information about all entities near the ship
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

    # Get all unowned planets
    entities_by_distance = [entities_by_distance[distance][0] for distance in entities_by_distance
                            if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                            not entities_by_distance[distance][0].is_owned() and
                            not entities_by_distance[distance][0] in planned_planets]

    # Find the closest unowned planet
    closest_planet = entities_by_distance[0]

    # Tell the ship to move to the planet
    if closest_planet is not None:
        # Get the move action of the ship
        return ship_control.move(ship, closest_planet, game_map, planned_planets)
