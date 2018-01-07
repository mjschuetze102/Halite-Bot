import hlt
import logging
import ship_functions as _ship
from collections import OrderedDict

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("BlackQueen v003")
# Then we print our start message to the logs
logging.info("Releasing the Black Queen!")

planned_planets = []
start_of_game = True
#turn_counter = -5

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()
    #turn_counter += 1

    #logging.info("Turn " + str(turn_counter))

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # Get my player object
    me = game_map.get_me()

    # Get all the ships that I own
    team_ships = game_map.get_me().all_ships()

    # Move ships away from each other at the start
    if start_of_game:
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

        # Send end of turn command queue
        game.send_command_queue(command_queue)
        start_of_game = False
        continue

    # For every ship that I control
    for ship in team_ships:

        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # Collect information about all entities near the ship
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        # Get the list of empty planets near the ship
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                                 if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                                 not entities_by_distance[distance][0].is_owned()]

        # Get the list of enemy ships near the ship
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance
                               if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                               entities_by_distance[distance][0] not in team_ships]

        # If there is an empty planet
        if len(closest_empty_planets) > 0:
            # Target the planet to move to
            target_planet = closest_empty_planets[0]

            # Get the list of closest allied planets to the target planet
            entities_by_distance = game_map.nearby_entities_by_distance(target_planet)
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
            closest_team_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                                    if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                                    entities_by_distance[distance][0].is_owner(me)]

            # If there are planets settled by me
            if len(closest_team_planets) > 0:
                #  Find the distance from the current ship to the target, and the closest planet to the target
                distance_to_target_from_ship = ship.calculate_distance_between(closest_empty_planets[0])
                distance_to_target_from_planet = closest_team_planets[0].calculate_distance_between(closest_empty_planets[0])

                # logging.info("Ship should {}\nDistance from ship: {}\nDistance from planet: {}".format(
                #     "expand" if distance_to_target_from_ship < (distance_to_target_from_planet + 30) else "dock",
                #     distance_to_target_from_ship, distance_to_target_from_planet))

                # If the ship is the closest entity I have to the target planet
                # +30 to try and account for ships spawning on far side of planet
                if distance_to_target_from_ship < (distance_to_target_from_planet + 30):
                    # logging.info("Ship {} is expanding".format(ship.id))

                    # Move the ship
                    (command_queue, planned_planets, cont) = _ship.move(ship, target_planet, command_queue,
                                                                        planned_planets, game_map)
                    if cont is 1:
                        continue

                # Else if I have a closer planet to the target planet
                # Try to dock at a planet to up production of ships
                elif distance_to_target_from_ship > distance_to_target_from_planet:
                    # logging.info("Ship {} is docking".format(ship.id))
                    # Get the list of closest allied planets to the target planet
                    entities_by_distance = game_map.nearby_entities_by_distance(ship)
                    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
                    closest_team_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                                            if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                                            entities_by_distance[distance][0].is_owner(me) and
                                            not entities_by_distance[distance][0].is_full()]

                    # If there are planets settled by me
                    if len(closest_team_planets) > 0:
                        # logging.info("Old ship target: " + str(target_planet))
                        # Target the planet to move to
                        target_planet = closest_team_planets[0]
                        # logging.info("New ship target: " + str(target_planet))

                        (command_queue, temp, cont) = _ship.move(ship, target_planet, command_queue, [], game_map)
                        if cont is 1:
                            continue

            # If I have not settled any planets yet
            else:
                # Target the planet to move to
                target_planet = next(planet for planet in closest_empty_planets if planet not in planned_planets)

                (command_queue, planned_planets, cont) = _ship.move(ship, target_planet, command_queue,
                                                                    planned_planets, game_map)
                if cont is 1:
                    continue

        # If there is no empty planet, but there are enemy ships
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]

            # Get the list of closest allied planets to the ship
            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
            closest_team_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                                    if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                                    entities_by_distance[distance][0].is_owner(me) and
                                    not entities_by_distance[distance][0].is_full()]

            # If there are planets that have not been fully docked
            if len(closest_team_planets) > 0:
                #  Find the distance from the current ship to the target ship and to the closest planet
                distance_to_target_ship = ship.calculate_distance_between(target_ship)
                distance_to_target_planet = ship.calculate_distance_between(closest_team_planets[0])

                # If the enemy ship is the closest entity to my ship
                # Attack the ship
                if distance_to_target_ship < distance_to_target_planet:
                    navigate_command = ship.navigate(
                        ship.closest_point_to(target_ship),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        angular_step=5,
                        ignore_ships=False
                    )

                    # If we can successfully navigate to the enemy, do so
                    if navigate_command:
                        command_queue.append(navigate_command)

                # Else if the ship is closer to the target planet
                # Try to dock at a planet to up production of ships
                elif distance_to_target_ship > distance_to_target_planet:
                    # Target the planet to move to
                    target_planet = closest_team_planets[0]

                    (command_queue, temp, cont) = _ship.move(ship, target_planet, command_queue, [], game_map)
                    if cont is 1:
                        continue

            # If all of my planets are fully docked
            else:
                # Attack the ship
                navigate_command = ship.navigate(
                    ship.closest_point_to(target_ship),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    angular_step=5,
                    ignore_ships=False
                )

                # If we can successfully navigate to the enemy, do so
                if navigate_command:
                    command_queue.append(navigate_command)

    # Send end of turn command queue
    game.send_command_queue(command_queue)

    # TURN END
# GAME END