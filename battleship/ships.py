# Battle Ship // Ship & Event classes
# Developed using Python 3

__author__ = "Hkaar"

__copyright__ = "Copyright (c) 2021 Hkaar"
__license__ = "GNU General Public License (GPL) V3"

"""This file is part of Battle Ship.

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

__version__ = 0.1

import random

class Event_Attack:
    def __init__(self, position, move_count, orientation):
        self.orientation = orientation
        self.move_count = move_count
        self.last_position = None
        self.position = position

class Event_Scout:
    def __init__(self, position, move_count, orientation):
        self.orientation = orientation
        self.move_count = move_count
        self.last_position = None
        self.position = position

class Patrol_Boat:
    def __init__(self, ship_name='Patrol Boat'):
        self.name = ship_name
        self.size = 2

        self.attack_cost = 4
        self.scout_cost = 4

    def get_attack(self, position, player_object):
        positions = ((position[0], position[1]-1), (position[0], position[1]+1), (position[0]-1, position[1]), (position[0]+1, position[1]))
        generated_positions = []

        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        for _ in range(0, 4):
            pos = random.choice(positions)
            if pos not in generated_positions:
                generated_positions.append(pos)

        return tuple(generated_positions)

    def get_scout(self, position, player_object):
        if player_object.available_positions > 0 and player_object.current_special_ship != 'aircraft_carrier':
            if position not in player_object.stored_positions:
                player_object.stored_positions.add(position)
                player_object.available_positions -= 1

            if player_object.available_positions <= 0:
                return True
        else:
            if player_object.__class__.__name__ != 'AI_Player':
                player_object.reset_positions()

            player_object.current_special_ship = 'patrol_boat'
            player_object.stored_positions.add(position)
            player_object.available_positions = 4
        return None

class Destroyer:
    def __init__(self, ship_name='Destroyer'):
        self.name = ship_name
        self.size = 3

        self.attack_cost = 3
        self.scout_cost = 3

    def get_attack(self, position, player_object):
        positions = ((position[0], position[1]-1), (position[0], position[1]+1), (position[0]-1, position[1]), (position[0]+1, position[1]))
        generated_positions = [position]

        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        for _ in range(0, 4):
            pos = random.choice(positions)
            if pos not in generated_positions and pos != position:
                generated_positions.append(pos)

        return tuple(generated_positions)

    def get_scout(self, position, player_object):
        positions = ((position[0], position[1]-1), (position[0], position[1]+1), (position[0]-1, position[1]), (position[0]+1, position[1]))
        generated_positions = [position]

        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        for _ in range(0, 5):
            pos = random.choice(positions)
            if pos not in generated_positions and pos != position:
                generated_positions.append(pos)

        return tuple(generated_positions)

class Submarine:
    def __init__(self, ship_name='Submarine'):
        self.name = ship_name
        self.size = 3

        self.attack_cost = 2
        self.scout_cost = 4

    def get_attack(self, position, player_object):
        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        event_torpedo_attack = Event_Attack(position, 1, player_object.orientation)
        player_object.add_event(event_torpedo_attack)
        return None

    def get_scout(self, position, player_object):
        positions = (
            (position[0]-1, position[1]-1), (position[0]-1, position[1]), (position[0]-1, position[1]+1),
            (position[0], position[1]-1), position, (position[0], position[1]+1)
            )
        generated_positions = []

        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        for _ in range(0, 6):
            pos = random.choice(positions)
            if pos not in generated_positions and pos != position:
                generated_positions.append(pos)

        return tuple(generated_positions)

class Battle_Ship:
    def __init__(self, ship_name='Battle Ship'):
        self.name = ship_name
        self.size = 4

        self.attack_cost = 5
        self.scout_cost = 5

    def get_attack(self, position, player_object):
        positions = (
            (position[0]-1, position[1]-1), (position[0]-1, position[1]), (position[0]-1, position[1]+1),
            (position[0], position[1]-1), position, (position[0], position[1]+1)
            )

        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        return positions

    def get_scout(self, position, player_object):
        positions = (
            (position[0]-1, position[1]-1), (position[0]-1, position[1]), (position[0]-1, position[1]+1),
            (position[0], position[1]-1), position, (position[0], position[1]+1)
            )

        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        return positions

class Aircraft_Carrier:
    def __init__(self, ship_name='Aircraft Carrier'):
        self.name = ship_name
        self.size = 5

        self.attack_cost = 8
        self.scout_cost = 5

    def get_attack(self, position, player_object):
        if player_object.available_positions > 0 and player_object.current_special_ship != 'patrol_boat':
            if position not in player_object.stored_positions:
                player_object.stored_positions.add(position)
                player_object.available_positions -= 1

            if player_object.available_positions <= 0:
                return True
        else:
            if player_object.__class__.__name__ != 'AI_Player':
                player_object.reset_positions()

            player_object.current_special_ship = 'aircraft_carrier'
            player_object.stored_positions.add(position)
            player_object.available_positions = 8
        return None

    def get_scout(self, position, player_object):
        if player_object.__class__.__name__ != 'AI_Player':
            player_object.reset_positions()

        event_airplane_scout = Event_Scout(position, 3, player_object.orientation)
        player_object.add_event(event_airplane_scout)
        return None