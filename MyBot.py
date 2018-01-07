import hlt
import logging
from collections import OrderedDict

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Settlerv003")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

planned_planets = []

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # Get all the ships that I own
    team_ships = game_map.get_me().all_ships()

    # For every ship that I control
    for ship in team_ships:
        # Get the ship ID
        shipid = ship.id

        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # Collect information about all entities near the ship
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        # Get the list of empty planets near the ship
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance \
                                 if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and \
                                 not entities_by_distance[distance][0].is_owned()]

        # Get the list of enemy ships near the ship
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance \
                               if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and \
                               entities_by_distance[distance][0] not in team_ships]

        # If there is an empty planet nearby
        if len(closest_empty_planets) > 0:
            # Target the planet to move to
            target_planet = closest_empty_planets[0]

            # If the ship can dock at the planet do so
            # Else navigate to the planet
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                # If the planet is already being navigated to ignore it
                # Else navigate to it
                if target_planet in planned_planets:
                    continue
                else:
                    navigate_command = ship.navigate(
                        ship.closest_point_to(target_planet),
                        game_map,
                        speed = int(hlt.constants.MAX_SPEED),
                        ignore_ships = False
                    )

                    # If we can successfully navigate to the planet, do so
                    if navigate_command:
                        command_queue.append(navigate_command)
                        planned_planets.append(target_planet)

        # If there is no empty planet, but there are enemy ships
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]

            navigate_command = ship.navigate(
                ship.closest_point_to(target_ship),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False
            )

            # If we can successfully navigate to the enemy, do so
            if navigate_command:
                command_queue.append(navigate_command)

    # Send end of turn command queue
    game.send_command_queue(command_queue)

    # TURN END
# GAME END