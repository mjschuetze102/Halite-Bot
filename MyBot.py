from collections import OrderedDict

import hlt
import logging
import ship_role_calculation as ship_role
import control_ship

# GAME START
# Here we define the bot's name and initialize the game, including communication with the Halite engine.
game = hlt.Game("BlackQueen v004")
# Then we print our start message to the logs
logging.info("Releasing the Black Queen!")

planned_planets = []
start_of_game = True

me = None
game_map = None

#####################################################
#      Define rules for figuring out ship role      #
#####################################################

calculate_new_ship_role = {
    hlt.entity.Ship.Role.NONE: lambda s, ce: ship_role.none_transition(s, ce, me),
    hlt.entity.Ship.Role.SETTLE: lambda s, ce: ship_role.settle_transition(s, ce, me),
    hlt.entity.Ship.Role.DOCK: lambda s, ce: ship_role.dock_transition(s, ce, me),
    hlt.entity.Ship.Role.ATTACK: lambda s, ce: ship_role.attack_transition(s, ce, me),
    hlt.entity.Ship.Role.DEFEND: lambda s, ce: ship_role.defend_transition(s, ce, me),
}

perform_ship_action = {
    hlt.entity.Ship.Role.SETTLE: lambda s, ce: control_ship.move(s, ce, game_map),
    hlt.entity.Ship.Role.DOCK: lambda s, ce: control_ship.move(s, ce, game_map),
    hlt.entity.Ship.Role.ATTACK: lambda s, ce: control_ship.attack(s, ce, game_map),
    hlt.entity.Ship.Role.DEFEND: lambda s, ce: control_ship.defend(s, ce, game_map),
}

#####################################################

while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # Get my player object
    me = game_map.get_me()

    # Get all the ships that I own
    team_ships = game_map.get_me().all_ships()

    # Move ships away from each other at the start
    if start_of_game:
        # Spread the ships apart at the start
        control_ship.scatter_ships(team_ships, command_queue)

        # Send end of turn command queue
        game.send_command_queue(command_queue)
        start_of_game = False

        for ship in team_ships:
            logging.info("Ship ID: {} Ship Role: {}".format(ship.id, ship.role))
        continue

    # For every ship that I control
    for ship in team_ships:

        # If the ship is docked
        if ship.docking_status is not ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        # Collect information about all entities near the ship
        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        # Get all entities excluding my other ships
        entities_by_distance = [entities_by_distance[distance][0] for distance in entities_by_distance
                                if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) or
                                (isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                                entities_by_distance[distance][0] not in team_ships)]

        # Find the closest entity to the ship
        closest_entity = entities_by_distance[0]

        # Calculate the new role for the ship
        calculate_new_ship_role[ship.role](ship, closest_entity)

        # Get the action the ship should perform
        action = perform_ship_action[ship.role](ship, closest_entity)

        # Make sure an action is performed
        if action is not None:
            # Execute commands based on the ships role
            command_queue.append(action)
        else:
            logging.info("No action was performed on Ship {} with Role {}".format(ship.id, ship.role))

    # Send end of turn command queue
    game.send_command_queue(command_queue)

    # TURN END
# GAME END