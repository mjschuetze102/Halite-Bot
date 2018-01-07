import hlt
import logging

def separate_ships(team_ships, command_queue):
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
        logging.info("Original role: " + str(ship.role))
        ship.change_role_settle()
        logging.info("Updated role: " + str(ship.role))

def move(ship, target_planet, command_queue, game_map):
    # If the ship can dock at the planet do so
    # Else navigate to the planet
    if ship.can_dock(target_planet):
        command_queue.append(ship.dock(target_planet))
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
            command_queue.append(navigate_command)