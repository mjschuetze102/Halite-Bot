import hlt
import logging

def move(ship, target_planet, command_queue, planned_planets, game_map):
    # If the ship can dock at the planet do so
    # Else navigate to the planet
    if ship.can_dock(target_planet):
        command_queue.append(ship.dock(target_planet))
    else:
        # If the planet is already being navigated to ignore it
        # Else navigate to it
        if target_planet in planned_planets:
            return command_queue, planned_planets, 1
        else:
            navigate_command = ship.navigate(
                ship.closest_point_to(target_planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False
            )

            # If we can successfully navigate to the planet, do so
            if navigate_command:
                command_queue.append(navigate_command)
                planned_planets.append(target_planet)

    return command_queue, planned_planets, 0