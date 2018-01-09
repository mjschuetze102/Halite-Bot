from collections import OrderedDict

import hlt
import logging
import ship_role_calculation as ship_role
import control_ship

# GAME START
# Here we define the bot's name and initialize the game, including communication with the Halite engine.
game = hlt.Game("BlackQueen v006")
# Then we print our start message to the logs
logging.info("Releasing the Black Queen!")

planned_planets = []
start_of_game = True

me = None
game_map = None

#####################################################
#      Define rules for figuring out ship role      #
#####################################################

my_fleet_roles = {}

calculate_new_ship_role = {
    hlt.entity.Ship.Role.NONE: lambda s, ce: ship_role.none_transition(s, ce, me),
    hlt.entity.Ship.Role.SETTLE: lambda s, ce: ship_role.settle_transition(s, ce, me),
    hlt.entity.Ship.Role.DOCK: lambda s, ce: ship_role.dock_transition(s, ce, me),
    hlt.entity.Ship.Role.ATTACK: lambda s, ce: ship_role.attack_transition(s, ce, me),
    hlt.entity.Ship.Role.DEFEND: lambda s, ce: ship_role.defend_transition(s, ce, me),
    hlt.entity.Ship.Role.DISTRACT: lambda s, ce: hlt.entity.Ship.Role.DISTRACT,
}

perform_ship_action = {
    hlt.entity.Ship.Role.SETTLE: lambda s, ce: control_ship.settle(s, planned_planets, game_map),
    hlt.entity.Ship.Role.DOCK: lambda s, ce: control_ship.move(s, ce, game_map),
    hlt.entity.Ship.Role.ATTACK: lambda s, ce: control_ship.attack(s, game_map),
    hlt.entity.Ship.Role.DEFEND: lambda s, ce: control_ship.defend(s, ce, game_map),
    hlt.entity.Ship.Role.DISTRACT: lambda s, ce: control_ship.distract(s, ce, game_map),
}

#####################################################

# my_bots = {}

#########################################################
# Check to see what role  the bots are getting stuck at #
#########################################################
# if ship.id in my_bots and my_bots[ship.id] is ship.role:
#     logging.info("Ship {} has kept {}".format(ship.id, ship.role))
#
# my_bots[ship.id] = ship.role
#########################################################

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

    # Get my player object
    me = game_map.get_me()

    # Get all the ships that I own
    team_ships = game_map.get_me().all_ships()

    # Move ships away from each other at the start
    if start_of_game:
        # Spread the ships apart at the start
        control_ship.scatter_ships(team_ships, command_queue)

        # Set the role of the first ship to DISTRACT
        team_ships[0].role = team_ships[0].Role.ATTACK

        for ship in team_ships:
            # Update the role of the current ship
            my_fleet_roles[ship.id] = ship.role

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
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance \
                                 if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and \
                                 not entities_by_distance[distance][0].is_owned() and
                                 not entities_by_distance[distance][0] in planned_planets]

        # Get all entities excluding my other ships
        entities_by_distance = [entities_by_distance[distance][0] for distance in entities_by_distance
                                if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) or
                                (isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                                entities_by_distance[distance][0] not in team_ships)]

        # Find the closest entity to the ship
        closest_entity = entities_by_distance[0]

        # Calculate the new role for the ship
        calculate_new_ship_role[ship.role](ship, closest_entity)

        if ship.role is ship.Role.SETTLE and not len(closest_empty_planets) > 0:
            ship.change_role_dock()

        logging.info("Ship {} has {}".format(ship.id, ship.role))

        # Get the action the ship should perform
        action = perform_ship_action[ship.role](ship, closest_entity)

        # Make sure an action is performed
        if action is not None:
            # Execute commands based on the ships role
            command_queue.append(action)
        else:
            logging.info("No action was performed on Ship {} with Role {}".format(ship.id, ship.role))

        # Update the role of the current ship
        my_fleet_roles[ship.id] = ship.role

        logging.info("Ship {} ending with {}".format(ship.id, ship.role))

    # Send end of turn command queue
    game.send_command_queue(command_queue)

    # TURN END
# GAME END