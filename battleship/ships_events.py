# Battle Ship // Ships & Events

__copyright__ = "Copyright (C) 2021-2022 Hkaar. All rights reserved."

__author__ = "Hkaar"
__version__ = "0.1.1"

__license__ = "GNU General Public License (GPL) V3"

"""
This file is part of Battle Ship.

Battle Ship is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

Battle Ship is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Battle Ship.  If not, see <https://www.gnu.org/licenses/>.
"""

import random

class Event:
    """An event class for certain classes of ship attacks"""
    def __init__(self, event_type, pos, dist, orientation="N"):
        self.orientation = orientation
        self.event_type = event_type 
        self.distance = dist

        self.last_pos = None
        self.pos = pos

class PatrolBoat:
    def __init__(self, name="Patrol Boat", randomize=True):
        self.get_name = lambda obj: obj.__class__.__name__

        self.name = name
        self.size = 2

        self.randomize = randomize
        self.pos_amount = 5

        self.attack_cost = 4
        self.scout_cost = 4

    def get_attack(self, pos, player_obj):
        if player_obj.orientation in ("N", "S"):
            positions = (pos, 
                (pos[0]+1, pos[1]), (pos[0]+2, pos[1]),
                (pos[0]-1, pos[1]), (pos[0]-2, pos[1])
                )
        else:
            positions = (pos, 
                (pos[0], pos[1]+1), (pos[0], pos[1]+2),
                (pos[0], pos[1]-1),  (pos[0], pos[1]-2)
                )

        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        if self.randomize:
            random_pos = set([])

            for _ in range(0, 5):
                random_pos.add(random.choice(positions))

            return random_pos
        return positions

    def get_scout(self, pos, player_obj):
        if self.get_name(player_obj.selected_ship) == "AttackWidget":
            selected_ship = player_obj.selected_ship.ship_obj
        else:
            selected_ship = player_obj.selected_ship

        if len(player_obj.stored_positions) > 0 and self.get_name(selected_ship) != "AircraftCarrier":
            if pos not in player_obj.stored_positions:
                player_obj.stored_positions.add(pos)

            if len(player_obj.stored_positions) >= self.pos_amount:
                return True

        else:
            if self.get_name(player_obj) != "AIPlayer":
                player_obj.stored_positions.clear()

            player_obj.stored_positions.add(pos)
        return None

class Destroyer:
    def __init__(self, name="Destroyer", randomize=True):
        self.get_name = lambda  obj: obj.__class__.__name__

        self.name = name
        self.size = 3

        self.randomize = randomize

        self.attack_cost = 3
        self.scout_cost = 3

    def get_attack(self, pos, player_obj):
        positions = (pos, 
            (pos[0], pos[1]-1), (pos[0], pos[1]+1),
            (pos[0]-1, pos[1]), (pos[0]+1, pos[1])
            )

        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        if self.randomize:
            random_pos = set([pos])

            for _ in range(0, 5):
                random_pos.add(random.choice(positions))
            return random_pos
        return positions

    def get_scout(self, pos, player_obj):
        positions = (pos, 
            (pos[0], pos[1]-1), (pos[0], pos[1]+1),
            (pos[0]-1, pos[1]), (pos[0]+1, pos[1])
            )

        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        if self.randomize:
            random_pos = set([pos])

            for _ in range(0, 5):
                random_pos.add(random.choice(positions))
            return random_pos
        return positions

class Submarine:
    def __init__(self, name="Submarine", randomize=True):
        self.get_name = lambda  obj: obj.__class__.__name__

        self.name = name
        self.size = 3

        self.randomize = randomize

        self.attack_cost = 2
        self.scout_cost = 4

    def get_attack(self, pos, player_obj):
        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        event_torpedo = Event("Attack", pos, 1, player_obj.orientation)
        player_obj.add_event(event_torpedo)

        return None

    def get_scout(self, pos, player_obj):
        positions = (
            (pos[0]-1, pos[1]-1), (pos[0]-1, pos[1]), (pos[0]-1, pos[1]+1),
            (pos[0], pos[1]-1), pos, (pos[0], pos[1]+1), 
            (pos[0]+1, pos[1]-1), (pos[0]+1, pos[1]), (pos[0]+1, pos[1]+1)
            )

        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        if self.randomize:
            random_pos = set([])

            for _ in range(0, 9):
                random_pos.add(random.choice(positions))

            return random_pos
        return positions

class BattleShip:
    def __init__(self, name="Battle Ship", randomize=False):
        self.get_name = lambda  obj: obj.__class__.__name__

        self.name = name
        self.size = 4

        self.randomize = randomize

        self.attack_cost = 5
        self.scout_cost = 5

    def get_attack(self, pos, player_obj):
        positions = (
            (pos[0]-1, pos[1]-1), (pos[0]-1, pos[1]), (pos[0]-1, pos[1]+1),
            (pos[0], pos[1]-1), pos, (pos[0], pos[1]+1)
            )

        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        if self.randomize:
            random_pos = set([])

            for _ in range(0, 9):
                random_pos.add(random.choice(positions))

            return random_pos
        return positions

    def get_scout(self, pos, player_obj):
        positions = (
            (pos[0]-1, pos[1]-1), (pos[0]-1, pos[1]), (pos[0]-1, pos[1]+1),
            (pos[0], pos[1]-1), pos, (pos[0], pos[1]+1)
            )

        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        if self.randomize:
            random_pos = set([])

            for _ in range(0, 9):
                random_pos.add(random.choice(positions))

            return random_pos
        return positions

class AircraftCarrier:
    def __init__(self, name="Battle Ship"):
        self.get_name = lambda  obj: obj.__class__.__name__

        self.name = name
        self.size = 5

        self.pos_amount = 9

        self.attack_cost = 7
        self.scout_cost = 5

    def get_attack(self, pos, player_obj):
        if self.get_name(player_obj.selected_ship) == "AttackWidget":
            selected_ship = player_obj.selected_ship.ship_obj
        else:
            selected_ship = player_obj.selected_ship

        if len(player_obj.stored_positions) > 0 and self.get_name(selected_ship) != "PatrolBoat":
            if pos not in player_obj.stored_positions:
                player_obj.stored_positions.add(pos)

            if len(player_obj.stored_positions) >= self.pos_amount:
                return True

        else:
            if self.get_name(player_obj) != "AIPlayer":
                player_obj.stored_positions.clear()

            player_obj.stored_positions.add(pos)
        return None

    def get_scout(self, pos, player_obj):
        if self.get_name(player_obj) != "AIPlayer":
            player_obj.stored_positions.clear()

        event_airplane = Event("Scout", pos, 3, player_obj.orientation)
        player_obj.add_event(event_airplane)

        return None
