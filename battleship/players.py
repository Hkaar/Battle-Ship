# Battle Ship // Players

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

import threading
import random

class Player:
    """Used for storing player game data"""
    def __init__(self, ship_manager, orientation='N'):
        self.attack_points = 0
        self.scout_points = 0

        self.orientation = orientation
        self.selected_ship = None
        self.mode = 'A'

        self.ship_manager = ship_manager

        self.deploy_piece_pos = {}
        self.attack_piece_pos = {}
        self.board_size = None
        self.ships_pos = {}

        self.player_widgets = {}

        self.undo_positions = {}
        self.undo_ships = {}
        self.redo_positions = {}
        self.redo_ships = {}

        self.stored_positions = set([])
        self.stored_hit_positions = {}
        self.stored_events = {}

    def add_widget(self, widget):
        """Adds a widget with an id to the player"""
        def generate_id():
            for gen_id in range(0, 99):
                if gen_id not in self.player_widgets:
                    return gen_id
            return None

        widget_id = gen_id()

        if widget_id != None:
            self.player_widgets[widget_id] = widget
            return True
        return False 

    def add_event(self, event):
        """Adds an event with an id to the player"""
        def generate_id():
            for gen_id in range(0, 999):
                if gen_id not in self.player_widgets:
                    return gen_id
            return None

        event_id = gen_id()

        if event_id != None:
            self.stored_events[event_id] = event
            return True
        return False

class AIPlayer:
    """Used for emulating player playing the game behaviour with storing its own
    game data"""
    def __init__(self, ship_manager, board_size=(7, 7)):
        self.attack_points = 0
        self.scout_points = 0

        self.selected_ship = None
        self.orientation = 'N'
        self.mode = 'A'

        self.ship_manager = ship_manager
        self.player_id = None

        self.deploy_piece_pos = tuple([(y, x) for y in range(0, board_size[0]) for x in range(0, board_size[1])])
        self.attack_piece_pos = tuple([(y, x) for y in range(0, board_size[0]) for x in range(0, board_size[1])])
        self.board_size = board_size
        self.ships_pos = {}

        self.memory = {'spotted': [], 'do_not_hit': []}
        
        self.stored_positions = set([])
        self.stored_hit_positions = {}
        self.stored_events = {}

        if board_size < (7, 7):
            raise ValueError("AI Player board size must be 7x7 or bigger!")

        self.gen_ships()

    def gen_ships(self):
        """Generates ships and automatically deploys them for use by the ai player for playing
        the game"""
        def deploy_ship(pos, ship_obj):
            """Deploys a ship on a board position"""
            positions = {}

            def add_pos(pos):
                if pos in self.deploy_piece_pos and pos not in self.ships_pos:
                    positions[pos] = ship_obj

            for size_num in range(0, ship_obj.size):
                if self.orientation == 'N':
                    gen_pos = (pos[0]-size_num, pos[1])
                elif self.orientation == 'W':
                    gen_pos = (pos[0], pos[1]-size_num)
                elif self.orientation == 'S':
                    gen_pos = (pos[0]+size_num, pos[1])
                else:
                    gen_pos = (pos[0], pos[1]+size_num)
                
                add_ship_pos(gen_pos)

            if len(positions) == ship_obj.size:
                self.ships_pos.update(positions)
            else:
                return False
            return True

        def deploy_ships():
            """Deploys all the ships by randomly choosing board positions & randomly choosing
            orientation"""
            ships = tuple(self.ship_manager.selected_ships.values())
            index = 0

            while index < 5:
                self.orientation = random.choice(("N", "W", "S", "E"))

                if deploy_ship(random.choice(self.deploy_piece_pos), ships[index]):
                    index += 1

        deployment_thread = threading.Thread(target=deploy_ships, daemon=True)
        deployment_thread.start()

    def exec_(self, target_piece_pos, attack_manager):
        """Makes the ai player choose a ship to either attack or scout a board position on
        the target players board"""
        get_name = lambda obj: obj.__class__.__name__

        def gen_pos(pos_amount):
            """Generates random positions based on how many positions need to be generated
            with the generated positions not already been hit"""
            while len(self.stored_positions) < pos_amount:
                pos = random.choice(target_piece_pos)

                if pos not in self.memory['do_not_hit']:
                    self.stored_positions.add(pos)

            return self.stored_positions

        def get_ship():
            """Gets a ship with enough points to attack or scout a board position"""
            ships = set([])

            for pos in self.ships_pos:
                ships.add(self.ships_pos[pos])

            for ship in ships:
                if self.mode == 'A' and ship.attack_cost > self.attack_points:
                    ships.remove(ship)

                elif self.mode == 'S' and ship.attack_cost > self.scout_points:
                    ships.remove(ship)

            if len(ships) > 0:
                return random.choice(tuple(ships))
            else:
                return None

        def exec_attacks():
            """Attacks or scouts all the stored positions that are stored by the ai player"""
            if len(self.stored_positions) > 0 and self.stored_positions:
                for pos in self.stored_positions:
                    if self.mode == 'A':
                        pos_val = attack_manager.exec_attack(pos, self.player_id)
                    else:
                        pos_val = attack_manager.exec_scout(pos, self.player_id)

                if pos_val == 2:
                    self.memory['spotted'].append(pos)
                else:
                    self.memory['do_not_hit'].append(pos)

            self.stored_positions.clear()

        attack_manager.exec_events(self.player_id)
        target_piece_pos = tuple(target_piece_pos)

        self.orientation = random.choice(('N', 'W', 'S', 'E'))
        self.mode = random.choice(('A', 'S'))

        if len(self.memory['spotted']) > 0:
            pos = random.choice(self.memory['spotted'])
        else:
            pos = random.choice([pos for pos in target_piece_pos if pos 
                not in self.memory['do_not_hit']])

        if attack_manager.abilities:
            self.selected_ship = get_ship()

            if (self.get_name(self.selected_ship) == "AircraftCarrier" and self.mode == "A") or (
                self.get_name(self.selected_ship) == "PatrolBoat" and self.mode == "S"):

                gen_pos_thread = threading.Thread(target=gen_pos, args=(self.selected_ship.pos_amount,), daemon=True)
                gen_pos_thread.start()
                gen_pos_thread.join()

            elif self.selected_ship != None:
                if self.mode == 'A':
                    self.stored_positions = self.selected_ship.get_attack(pos, self)
                else:
                    self.stored_positions = self.selected_ship.get_scout(pos, self)

                if pos in self.memory['spotted']:
                    self.memory['spotted'].remove(pos) 

            else:
                self.stored_positions.add(pos)

                if pos in self.memory['spotted']:
                    self.memory['spotted'].remove(pos)

            exec_attacks()
        else:
            attack_manager.exec_attack(pos, self.player_id)

    def add_event(self, event):
        """Adds an event with an id to the player"""
        def generate_id():
            for gen_id in range(0, 999):
                if gen_id not in self.player_widgets:
                    return gen_id
            return None

        event_id = gen_id()

        if event_id != None:
            self.stored_events[event_id] = event
            return True
        return False
