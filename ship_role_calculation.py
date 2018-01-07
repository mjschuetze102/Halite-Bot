import hlt
import logging

#
# TODO: change from 4 functions to 1 with each if statement having a dict for state transition

def settle_transition(ship, closest_entity, me):
    """
    Compute logic for ships set to settle
    :param ship: entity to control
    :param closest_entity: object that is closest to current ship
    :param me: my player object
    """
    # Determine if closest entity is a planet
    if isinstance(closest_entity, hlt.entity.Planet):
        # Determine if planet is unowned
        if not closest_entity.is_owned():
            """
            If closest planet is now unowned,
            then we can still settle
            """
            # No need to change state
            return

        # If the planet is owned, but not by me
        elif not closest_entity.is_owner(me):
            """
            If closest planet is now not unowned,
            then someone else has settled it and we attack
            """
            ship.change_role_attack()

        # If the planet is owned by me
        else:
            # If the planet still has space to mine
            if not closest_entity.is_full():
                """
                If closest planet is now owned by me and not full,
                then dock to create more ships
                """
                ship.change_role_dock()

            # If the planet does not have space to mine
            else:
                """
                If closest planet is now owned by me and full,
                then defend the planet
                """
                ship.change_role_defend()

    # Determine if closest entity is a ship
    elif isinstance(closest_entity, hlt.entity.Ship):
        """
        If closest entity is now a ship,
        then defend so we can settle later
        """
        ship.change_role_defend()

    else:
        logging.info("Unknown type: " + str(closest_entity))


def dock_transition(ship, closest_entity, me):
    """
        Compute logic for ships set to dock
        :param ship: entity to control
        :param closest_entity: object that is closest to current ship
        :param me: my player object
        """
    # Determine if closest entity is a planet
    if isinstance(closest_entity, hlt.entity.Planet):
        # Determine if planet is unowned
        if not closest_entity.is_owned():
            """
            If closest planet is now unowned,
            then defend because the current planet is contested
            """
            ship.change_role_defend()

        # If the planet is owned, but not by me
        elif not closest_entity.is_owner(me):
            """
            If closest planet is now owned by someone else,
            then attack because the current planet has been taken
            """
            ship.change_role_attack()

        # If the planet is owned by me
        else:
            # If the planet still has space to mine
            if not closest_entity.is_full():
                """
                If closest planet is now owned by me and not full,
                then we can still dock
                """
                # No need to change state
                return

            # If the planet does not have space to mine
            else:
                """
                If closest planet is now owned by me and full,
                then defend the planet
                """
                ship.change_role_defend()

    # Determine if closest entity is a ship
    elif isinstance(closest_entity, hlt.entity.Ship):
        """
        If closest entity is now a ship,
        then defend so we can settle later
        """
        ship.change_role_defend()

    else:
        logging.info("Unknown type: " + str(closest_entity))


def attack_transition(ship, closest_entity, me):
        """
            Compute logic for ships set to attack
            :param ship: entity to control
            :param closest_entity: object that is closest to current ship
            :param me: my player object
            """
        # Determine if closest entity is a planet
        if isinstance(closest_entity, hlt.entity.Planet):
            # Determine if planet is unowned
            if not closest_entity.is_owned():
                """
                If closest planet is now unowned,
                then defend the planet so we can settle later
                """
                ship.change_role_defend()

            # If the planet is owned, but not by me
            elif not closest_entity.is_owner(me):
                """
                If closest planet is now not unowned,
                then attack the planet to remove the enemy
                """
                # No need to change state
                return

            # If the planet is owned by me
            else:
                # If the planet still has space to mine
                if not closest_entity.is_full():
                    """
                    If closest planet is now owned by me and not full,
                    then continue attacking
                    """
                    # No need to change state
                    return

                # If the planet does not have space to mine
                else:
                    """
                    If closest planet is now owned by me and full,
                    then continue attacking
                    """
                    # No need to change state
                    return

        # Determine if closest entity is a ship
        elif isinstance(closest_entity, hlt.entity.Ship):
            """
            If closest entity is now a ship,
            then continue attacking
            """
            # No need to change state
            return

        else:
            logging.info("Unknown type: " + str(closest_entity))


def defend_transition(ship, closest_entity, me):
    """
        Compute logic for ships set to defend
        :param ship: entity to control
        :param closest_entity: object that is closest to current ship
        :param me: my player object
        """
    # Determine if closest entity is a planet
    if isinstance(closest_entity, hlt.entity.Planet):
        # Determine if planet is unowned
        if not closest_entity.is_owned():
            """
            If closest planet is now unowned,
            then continue to defend
            """
            # TODO change to suicide into the planet?
            # No need to change state
            return

        # If the planet is owned, but not by me
        elif not closest_entity.is_owner(me):
            """
            If closest planet is now not unowned,
            then take the planet over
            """
            # TODO perhaps keep it defended so we eliminate enemy ships
            ship.change_role_attack()

        # If the planet is owned by me
        else:
            # If the planet still has space to mine
            if not closest_entity.is_full():
                """
                If closest planet is now owned by me and not full,
                then continue to defend while we wait for ships to dock
                """
                # No need to change state
                return

            # If the planet does not have space to mine
            else:
                """
                If closest planet is now owned by me and full,
                then go attack as this planet is well defended
                """
                ship.change_role_attack()

    # Determine if closest entity is a ship
    elif isinstance(closest_entity, hlt.entity.Ship):
        """
        If closest entity is now a ship,
        then continue to defend the planet
        """
        # No need to change state
        return

    else:
        logging.info("Unknown type: " + str(closest_entity))