from collections import OrderedDict

import hlt
import logging


def scatter_ships(team_ships, command_queue):
    # For every ship that I control
    for ship in team_ships:
        # Collect the position of the other ships
        ally_ship_position = []
        for ally in team_ships:
            if ally is not ship:
                ally_ship_position.append(ship.calculate_angle_between(ally))

        # Find the middle of the two other ships
        thrust_direction = int(180 + (sum(ally_ship_position) / len(ally_ship_position)))

        # Move the ship away from the others
        thrust_command = ship.thrust(hlt.constants.MAX_SPEED, thrust_direction)
        command_queue.append(thrust_command)

        # Tell the ship to SETTLE
        ship.change_role_settle()


def move(ship, target_planet, game_map, planned_planets = None):
    """
    Moves the ship towards target_planet
    :param ship: current ship being controlled
    :param target_planet: destination for the ship
    :param game_map: the map of the game
    :param planned_planets: list of empty planets being traveled to
    :return: action to be entered into command_queue
    """
    # If the ship can dock at the planet do so
    if ship.can_dock(target_planet):
        # # Remove the planet from planned planets
        # if planned_planets is not None:
        #     planned_planets.remove(target_planet)
        #     logging.info("Planet {} was removed from planned planets".format(target_planet.id))
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
            # Add the planet to planned planets
            if planned_planets is not None:
                planned_planets.append(target_planet)
            #     if target_planet not in planned_planets:
            #         planned_planets.append(target_planet)
            #         logging.info("Planet {} was added to planned planets".format(target_planet.id))
            return navigate_command


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
        return move(ship, closest_planet, game_map, planned_planets)


def destroy(ship, target_ship, game_map):
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


def attack(ship, game_map):
    """
    Moves the ship towards the enemy ship
    :param ship: current ship being controlled
    :param target_ship: destination for the ship
    :param game_map: the map of the game
    :return: action to be entered into command_queue
    """
    # Collect information about all entities near the ship
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

    # Get all entities excluding my ships and other planets
    entities_by_distance = [entities_by_distance[distance][0] for distance in entities_by_distance
                            if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                            entities_by_distance[distance][0] not in game_map.get_me().all_ships()]

    # Find the closest enemy
    closest_enemy = entities_by_distance[0]

    if closest_enemy is not None:
        # Destroy the enemy
        return destroy(ship, closest_enemy, game_map)


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
        return destroy(ship, target, game_map)

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
            # Destroy the enemy
            return destroy(ship, closest_enemy, game_map)

    # If the target is not an enemy ship or planet
    else:
        logging.info("Unknown type: " + str(target))