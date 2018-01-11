import logging
from collections import OrderedDict

import hlt
import AI_BRAIN_007

# GAME START
# Here we define the bot's name and initialize the game, including communication with the Halite engine.
game = hlt.Game("BlackQueen v007")
# Then we print our start message to the logs
logging.info("Releasing the Black Queen!")

#####################################################
#         Define rules for storing ship role        #
#####################################################

my_fleet_roles = {}
planned_planets = []
start_of_game = True

NEARBY = 40.0
FAR_AWAY = 80.0


#####################################################


def turn_one():
    for bot in team_ships:
        # Collect the position of the other ships
        ally_ship_position = []
        for ally in team_ships:
            if ally is not bot:
                ally_ship_position.append(bot.calculate_angle_between(ally))

        # Find the middle of the two other ships
        thrust_direction = int(180 + (sum(ally_ship_position) / len(ally_ship_position)))

        # Move the ship away from the others
        thrust_command = bot.thrust(hlt.constants.MAX_SPEED, thrust_direction)
        command_queue.append(thrust_command)

        bot.change_role_start()

    # Figure out whether to attack the enemy with my first ship or not
    enemy = AI_BRAIN_007.ship_logic.get_closest_enemy(team_ships[0], game_map)

    if team_ships[0].calculate_distance_between(enemy) < FAR_AWAY:
        # Set the role of the first ship to DISTRACT
        team_ships[0].role = team_ships[0].Role.ATTACK

    for bot in team_ships:
        # Update the role of the current ship
        my_fleet_roles[bot.id] = bot.role

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # Clear the list of planned planets to speed up process
    # Each iteration uses a copy of the planet not the reference to it
    # By clearing the list, we aren't actually changing functionality
    planned_planets = []

    # Get all the ships that I own
    team_ships = game_map.get_me().all_ships()

    # Move ships away from each other at the start
    if start_of_game:
        # Spread the ships apart at the start
        turn_one()

        # Send end of turn command queue
        game.send_command_queue(command_queue)
        start_of_game = False
        continue

    # For every ship that I control
    for ship in team_ships:
        # Find the role of the current ship
        if ship.id in my_fleet_roles:
            ship.role = my_fleet_roles[ship.id]

        logging.info("Ship {} starting with {}".format(ship.id, ship.role))

        # If the ship is docked
        if ship.docking_status is not ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # Collect information about all entities near the ship
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        # Get the list of empty planets near the ship
        closest_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                           if isinstance(entities_by_distance[distance][0], hlt.entity.Planet)]

        # Find the closest planet to the ship
        closest_planet = closest_planets[0]

        # Get the list of empty planets near the ship
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                                 if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                                 not entities_by_distance[distance][0].is_owned() and
                                 not entities_by_distance[distance][0] in planned_planets]

        ######################################################
        #       Calculating the new role for the ship        #
        ######################################################

        # Get the list of closest entities
        entities_by_distance = [entities_by_distance[distance][0] for distance in entities_by_distance
                                if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) or
                                (isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                                 entities_by_distance[distance][0] not in team_ships)]

        # Find the closest entity to the ship
        closest_entity = entities_by_distance[0]

        entity_type = None
        if isinstance(closest_entity, hlt.entity.Ship):
            entity_type = AI_BRAIN_007.ship_role.ClosestEntity.ENEMY_SHIP

        elif not closest_entity.is_owned():
            entity_type = AI_BRAIN_007.ship_role.ClosestEntity.EMPTY_PLANET

        elif not closest_entity.is_owner(game_map.get_me()):
            entity_type = AI_BRAIN_007.ship_role.ClosestEntity.ENEMY_PLANET

        elif not closest_entity.is_full():
            entity_type = AI_BRAIN_007.ship_role.ClosestEntity.FILLING_PLANET

        elif closest_entity.is_full():
            entity_type = AI_BRAIN_007.ship_role.ClosestEntity.FULL_PLANET

        # Calculate the new role for the ship
        AI_BRAIN_007.ship_role.calculate_new_ship_role[entity_type](ship)

        if ship.role is ship.Role.SETTLE and not len(closest_empty_planets) > 0:
            ship.change_role_dock()

        ######################################################

        logging.info("Ship {} has {}".format(ship.id, ship.role))

        ######################################################
        #      Calculating the next action for the ship      #
        ######################################################

        # Find the closest_enemy to the current ship
        closest_enemy = AI_BRAIN_007.ship_logic.get_closest_enemy(ship, game_map)

        # Figure out how far away the enemy is
        distance_to_enemy = ship.calculate_distance_between(closest_enemy)

        enemy_distance = None
        if distance_to_enemy <= NEARBY:
            enemy_distance = AI_BRAIN_007.ship_logic.EnemyCloseness.NEARBY

        elif NEARBY < distance_to_enemy < FAR_AWAY:
            enemy_distance = AI_BRAIN_007.ship_logic.EnemyCloseness.ON_RADAR

        elif FAR_AWAY <= distance_to_enemy:
            enemy_distance = AI_BRAIN_007.ship_logic.EnemyCloseness.FAR_AWAY

        # Get the action the ship should perform
        action = AI_BRAIN_007.ship_logic.perform_ship_action[enemy_distance](ship, game_map, closest_enemy,
                                                                             closest_planet, planned_planets)

        # Make sure an action is performed
        if action is not None:
            # Execute commands based on the ships role
            command_queue.append(action)
        else:
            logging.info("No action was performed on Ship {} with Role {}".format(ship.id, ship.role))

        ######################################################

        # Update the role of the current ship
        my_fleet_roles[ship.id] = ship.role

        logging.info("Ship {} ending with {}".format(ship.id, ship.role))

    # Send end of turn command queue
    game.send_command_queue(command_queue)

    # TURN END
# GAME END