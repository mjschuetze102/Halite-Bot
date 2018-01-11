from enum import Enum
from random import randint

import hlt


class ClosestEntity(Enum):
    EMPTY_PLANET = 0
    ENEMY_PLANET = 1
    FILLING_PLANET = 2
    FULL_PLANET = 3
    ENEMY_SHIP = 4

not_owned_planet = {
    hlt.entity.Ship.Role.NONE: lambda s: s.change_role_settle(),
    hlt.entity.Ship.Role.START: lambda s: None,
    hlt.entity.Ship.Role.SETTLE: lambda s: None,
    hlt.entity.Ship.Role.DOCK: lambda s: s.change_role_settle(),
    hlt.entity.Ship.Role.ATTACK: lambda s: None,
    hlt.entity.Ship.Role.DEFEND: lambda s: None,
}

enemy_planet = {
    hlt.entity.Ship.Role.NONE: lambda s: s.change_role_attack(),
    hlt.entity.Ship.Role.START: lambda s: s.change_role_attack(),
    hlt.entity.Ship.Role.SETTLE: lambda s: s.change_role_attack(),
    hlt.entity.Ship.Role.DOCK: lambda s: s.change_role_attack(),
    hlt.entity.Ship.Role.ATTACK: lambda s: None,
    hlt.entity.Ship.Role.DEFEND: lambda s: s.change_role_attack(),
}

not_full_ally_planet = {
    hlt.entity.Ship.Role.NONE: lambda s: s.change_role_dock() if randint(0, 1) else s.change_role_settle(),
    hlt.entity.Ship.Role.START: lambda s: None,
    hlt.entity.Ship.Role.SETTLE: lambda s: None,
    hlt.entity.Ship.Role.DOCK: lambda s: None,
    hlt.entity.Ship.Role.ATTACK: lambda s: s.change_role_dock(),
    hlt.entity.Ship.Role.DEFEND: lambda s: None,
}

full_ally_planet = {
    hlt.entity.Ship.Role.NONE: lambda s: s.change_role_settle(),
    hlt.entity.Ship.Role.START: lambda s: s.change_role_settle(),
    hlt.entity.Ship.Role.SETTLE: lambda s: None,
    hlt.entity.Ship.Role.DOCK: lambda s: s.change_role_attack(),
    hlt.entity.Ship.Role.ATTACK: lambda s: None,
    hlt.entity.Ship.Role.DEFEND: lambda s: s.change_role_attack(),
}

enemy_ship = {
    hlt.entity.Ship.Role.NONE: lambda s: s.change_role_defend(),
    hlt.entity.Ship.Role.START: lambda s: s.change_role_defend(),
    hlt.entity.Ship.Role.SETTLE: lambda s: s.change_role_defend(),
    hlt.entity.Ship.Role.DOCK: lambda s: s.change_role_defend(),
    hlt.entity.Ship.Role.ATTACK: lambda s: None,
    hlt.entity.Ship.Role.DEFEND: lambda s: s.change_role_attack(),
}

#################################################
#  Decides which dictionary to get values from  #
#################################################

calculate_new_ship_role = {
    ClosestEntity.EMPTY_PLANET: lambda s: not_owned_planet[s.role](s),
    ClosestEntity.ENEMY_PLANET: lambda s: enemy_planet[s.role](s),
    ClosestEntity.FILLING_PLANET: lambda s: not_full_ally_planet[s.role](s),
    ClosestEntity.FULL_PLANET: lambda s: full_ally_planet[s.role](s),
    ClosestEntity.ENEMY_SHIP: lambda s: enemy_ship[s.role](s),
}

#################################################
