import hlt
import logging


def move(ship, target_planet, game_map, planned_planets=None):
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
            return navigate_command


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


def retreat(ship, target_ship):
    """
        Move the ship away from the target
        :param ship: current ship being controlled
        :param target_ship: enemy closest to the ship
        :return: action to be entered into command_queue
        """
    # Set the speed the ship will travel at
    speed = hlt.constants.MAX_SPEED

    # Calculate the angle between the ship and target
    angle_to_target = ship.calculate_angle_between(target_ship)

    # Calculate the angle to run away at
    angle = angle_to_target + 180

    return ship.thrust(speed, angle)


def investigate(ship, target):
    """
    Move the ship just outside the range of the target
    :param ship: current ship being controlled
    :param target: destination for the ship
    :param game_map: the map of the game
    :return: action to be entered into command_queue
    """
    # Set the speed the ship will travel at
    speed = hlt.constants.MAX_SPEED

    # Calculate the distance between the ship and target's range
    distance = ship.calculate_distance_between(target) - (hlt.constants.SHIP_RADIUS + hlt.constants.WEAPON_RADIUS)

    # Calculate the angle between the ship and target
    angle = ship.calculate_angle_between(target)

    # Figure out how how fast the ship needs to travel to the target
    speed = speed if (distance >= speed) else distance

    return ship.thrust(speed, angle)
