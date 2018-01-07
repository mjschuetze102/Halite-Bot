from collections import OrderedDict

import hlt
import logging

def move(ship, target_planet, game_map):
    """
    Moves the ship towards target_planet
    :param ship: current ship being controlled
    :param target_planet: destination for the ship
    :param game_map: the map of the game
    :return: action to be entered into command_queue
    """
    # If the ship can dock at the planet do so
    if ship.can_dock(target_planet):
        return ship.dock(target_planet)
    # Navigate to the planet
    else:
        navigate_command = ship.navigate(
            ship.closest_point_to(target_planet),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            angular_step=5,
            ignore_ships=False
        )

        # If we can successfully navigate to the planet, do so
        if navigate_command:
            return navigate_command


def attack(ship, target_ship, game_map):
    """
    Moves the ship towards the enemy ship
    :param ship: current ship being controlled
    :param target_ship: destination for the ship
    :param game_map: the map of the game
    :return: action to be entered into command_queue
    """
    # Navigate to the ship
    navigate_command = ship.navigate(
        ship.closest_point_to(target_ship),
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        angular_step=5,
        ignore_ships=False
    )

    # If we can successfully navigate to the planet, do so
    if navigate_command:
        return navigate_command


def defend(ship, target, game_map):
    """
    Moves the ship towards the target
    :param ship: current ship being controlled
    :param target: destination for the ship
    :param game_map: the map of the game
    :return: action to be entered into command_queue
    """
    # If the target is an enemy ship, attack it
    if isinstance(target, hlt.entity.Ship):
        return attack(ship, target, game_map)

    # If the target is a planet
    elif isinstance(target, hlt.entity.Planet):
        """
        Find the enemy closest to the planet to attack
        The enemy must be within a certain range of current planet
        """
        # Collect information about all entities near the ship
        entities_by_distance = game_map.nearby_entities_by_distance(target)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        # Get all entities excluding my ships and other planets
        entities_by_distance = [entities_by_distance[distance][0] for distance in entities_by_distance
                                if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                                entities_by_distance[distance][0] not in game_map.get_me().all_ships()]

        # Find the closest enemy to the planet
        closest_enemy = entities_by_distance[0] \
            if target.calculate_distance_between(entities_by_distance[0]) < (target.radius * 2) else None

        if closest_enemy is not None:
            # Attack the enemy
            return attack(ship, closest_enemy, game_map)

    # If the target is not an enemy ship or planet
    else:
        logging.info("Unknown type: " + str(target))