# Battle Ship // Managers

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
import configparser
import json

import gc

from ships_events import PatrolBoat, Destroyer, Submarine, BattleShip, AircraftCarrier
from pathlib import Path

class DeployManager:
    """Manages the players ship deployment, and deployment status in the game during the 
    deployment phase"""
    def __init__(self, player_amount, player_objs, attack_manager, windows=None):
        self.get_name = lambda obj: obj.__class__.__name__

        self.attack_manager = attack_manager
        self.windows = windows

        self.deploy_status = {}
        self.player_objs = {}

        self.gen_players(player_amount, player_objs)

    def gen_players(self, amount, player_objs):
        """Generates an id and sets deployment status for all the player objects"""
        if amount == len(player_objs):
            for gen_id in range(0, amount):
                self.player_objs[gen_id] = player_objs[gen_id]

                if self.get_name(player_objs[gen_id]) == "AIPlayer":
                    self.deploy_status[gen_id] = True
                else:
                    self.deploy_status[gen_id] = False

        else:
            raise ValueError("Amount of players is not equal to the amount of player objects!")

    def end_deployment(self, player):
        """Ends deployment for a player and checks if all players already ended deployment"""
        def check_deployment():
            """Checks if all players have already ended deployment"""
            for player_id in self.deploy_status:
                if not self.deploy_status[player_id]:
                    return False
            return True

        if player in self.player_objs and not self.deploy_status[player]:
            if len(self.deploy_status[player].ships_pos) > 0:
                self.deploy_status[player] = True

                for pos in self.player_objs[player].deploy_piece_pos:
                    self.player_objs[player].deploy_piece_pos[pos].setEnabled(False)

                if check_deployment():
                    self.close()
            else:
                return False
        return True

    def undo_deployment(self, player):
        """Undoes ship deployment / placement on the board by a player"""
        def generate_id(player_obj):
            for gen_id in range(0, 99):
                if gen_id not in player_obj.redo_positions:
                    return gen_id
            return None

        if player in self.player_objs and not self.deploy_status[player]:
            player_obj = self.player_objs[player]

            if len(player_obj.undo_positions) > 0:
                undo_id = len(player.undo_positions)-1
                redo_id = generate_id(player_obj)

                if self.get_name(player_obj.undo_ships[undo_id]) == "DeployWidget":
                    player_obj.undo_ships[undo_id].setEnabled(True)

                player_obj.selected_ship = player_obj.undo_ships[undo_id]

                for pos in player_obj.undo_positions[undo_id]:
                    player_obj.deploy_piece_pos[pos].setText(' ')
                    player_obj.deploy_piece_pos[pos].setEnabled(True)
                    player_obj.ships_pos.pop(pos,)

                player_obj.redo_positions[redo_id] = player_obj.undo_positions[undo_id]
                player_obj.redo_ships[redo_id] = player_obj.undo_ships[undo_id]

                player_obj.undo_positions.pop(undo_id,)
                player_obj.undo_ships.pop(undo_id,)

            else:
                player_obj.undo_positions.clear()
                player_obj.undo_ships.clear()

    def redo_deployment(self, player):
        """Redoes ship deployment / placement on the board by a player"""
        def generate_id(player_obj):
            for gen_id in range(0, 99):
                if gen_id not in player_obj.undo_positions:
                    return gen_id
            return None 

        if player in self.player_objs and not self.deploy_status[selected_player]:
            player_obj = self.player_objs[player]

            if len(player_obj.redo_positions) > 0:
                redo_id = len(player_obj.redo_positions)-1
                undo_id = generate_id(player_obj)

                if self.get_name(player_obj.redo_ships[redo_id]) == "DeployWidget":
                    player_obj.redo_ships[redo_id].setEnabled(False)

                player_obj.selected_ship = None

                for pos in player_obj.redo_positions[redo_id]:
                    player_obj.deploy_piece_pos[pos].setText('[]')
                    player_obj.deploy_piece_pos[pos].setEnabled(False)
                    player_obj.ships_pos[pos] = player_obj.redo_positions[redo_id][pos]

                player_obj.undo_positions[undo_id] = player_obj.redo_positions[redo_id]
                player_obj.undo_ships[undo_id] = player_obj.redo_ships[redo_id]

                player_obj.redo_positions[redo_id].pop(redo_id,)
                player_obj.redo_ships[redo_id].pop(redo_id,)

            else:
                player_obj.redo_positions.clear()
                player_obj.redo_ships.clear()

    def reset(self, player_amount, player_objs, windows=None):
        """Resets the manager to accept new players"""
        self.player_objs.clear()
        self.deploy_status.clear()

        if self.windows:
            self.windows.clear()

        self.gen_players(player_amount, player_objs)

    def show(self):
        """Shows all the stored player deployment windows"""
        if self.windows != None:
            for win in self.windows:
                win.show()
        return None

    def close(self):
        """Closes all the stored player deployment windows, and shows all the stored player 
        attack windows in attack manager"""
        if self.windows != None:
            for win in self.windows:
                win.close()
                
            self.attack_manager.show()
        return None

class AttackManager:
    """Manages the players turn, target and ship attacks in the game during the attacking phase"""
    def __init__(self, player_amount, player_objs, windows=None, close_func=None, enable_abilities=False):
        self.get_name = lambda obj: obj.__class__.__name__

        self.ablities = enable_abilities
        self.close_func = close_func
        self.windows = {}

        self.results = {}
        self.turn = 0

        self.disabled_player_obj = None
        self.player_objs = {}
        self.player_targets = {}

        self.gen_players(player_amount, player_objs, windows)

    def gen_players(self, amount, player_objs, windows):
        """Generates ids and sets the targets, attack & scout points for all the player objects"""
        self.turn = random.randint(1, amount)
        
        if amount == len(player_objs):
            for gen_id in range(0, amount):
                self.player_objs[gen_id] = player_objs[gen_id]

                if self.get_name(player_objs[gen_id]) == "AIPlayer":
                    player_objs[gen_id].player_id = gen_id

                if gen_id != self.turn:
                    player_objs[gen_id].attack_points += 1
                    player_objs[gen_id].scout_points += 1
                else:
                    player_objs[gen_id].attack_points += 3
                    player_objs[gen_id].scout_points += 3

                if gen_id+2 <= amount:
                    self.player_targets[gen_id] = gen_id+1
                else:
                    self.player_targets[gen_id] = gen_id+1-amount

                self.windows[gen_id] = windows[gen_id]

        else:
            raise ValueError("Amount of players is not equal to the amount of player objects!")

    def check_widgets(self):
        """Checks if all the player widgets are still present on the board"""
        def check_player_widgets(player_obj):
            if self.get_name(player_obj) != "AIPlayer":
                ships = set(ships_pos.values())

                for w_id in player_obj.stored_widgets:
                    if player_obj.stored_widgets[w_id].ship_obj not in ships:
                        player_obj.stored_widgets[w_id].setEnabled(False)
            return None

        for player_id in self.player_objs:
            check_player_widgets(self.player_objs[player_id])

    def next_target(self, player):
        """Goes to the next target for a player and loads the target player hit positions. 
        Does not work if there are no available player targets"""
        def get_next_target():
            """Gets the next available player target, returns none if there are no available
            player targets"""
            targeted_players = tuple(self.player_targets.values())

            for player_id in self.player_targets:
                if player_id not in targeted_players:
                    return player_id
            return None

        def load_hit_positions(player):
            """Loads all the target players positions that already been hit"""
            if self.player_targets.get(player):
                target_hit_pos = self.player_objs[self.player_targets[player]].stored_hit_positions
            else:
                target_hit_pos = self.disabled_player_obj.stored_hit_positions

            piece_pos = self.player_objs[player].attack_piece_pos
            piece_translations = {0: '\u25FB', 1: '\u25FC', 2: '\u25A3'}

            for pos in piece_pos:
                piece_pos[pos].setText(' ')
                piece_pos[pos].setEnabled(True)

            for pos in target_hit_pos:
                if pos in piece_pos and target_hit_pos[pos] in piece_translations:
                    piece_pos[pos].setText(piece_translations[target_hit_pos[pos]])

                    if target_hit_pos[pos] == 1:
                        piece_pos[pos].setEnabled(False)
            return None

        next_target = get_next_target()

        if len(self.player_objs) > 1 and player in self.player_objs and next_target != None:
            self.player_objs[player].stored_events.clear()
            self.player_targets[player] = next_target

            if self.get_name(self.player_objs[player]) != "AIPlayer":
                load_hit_positions(player)

    def next_turn(self, player):
        """Goes to the next player turn, fails if the player requesting is not the current turn"""
        def get_next_player():
            """Gets the next player, returns the first player if the current turn is the last player"""
            players = tuple(self.player_objs.keys())

            if self.player_objs.get(self.turn) and self.get_name(self.player_objs[self.turn]) != "AIPlayer":
                self.player_objs[self.turn].stored_positions.clear()

            for player_id in players:
                if player_id == players[len(self.player_objs)-1] and self.turn == player_id:
                    return players[0]

                elif player_id > self.turn:
                    return player_id
            return None

        def goto_next_player():
            """Changes the turn to the next player, executes the next player object if the player object is an AI"""
            while True:
                next_player = get_next_player()
                player_obj = self.player_objs[next_player]

                if len(self.player_objs) > 1 and next_player != None and len(player_obj.ships_pos) > 0:
                    if self.get_name(player_obj) != "AIPlayer":
                        player_obj.exec_(self.player_objs[self.player_targets[next_player]].attack_piece_pos, self)
                        self.turn = next_player
                    else:
                        self.turn = next_player
                        break

                elif len(self.player_objs) > 1 and len(player_obj.ships_pos) <= 0:
                    self.turn = next_player

                else:
                    break

        if player == self.turn:
            next_turn_thread = threading.Thread(target=goto_next_player, daemon=True)
            next_turn_thread.start()
            next_turn_thread.join()

            if self.abilities and self.turn in self.player_objs:
                self.player_objs[self.turn].attack_points += 3
                self.player_objs[self.turn].scout_points += 3

                self.exec_events(self.turn)

            self.check_widgets()
            return True
        return False

    def is_player_target_alive(self, player):
        """Checks if the players target is still alive / still has ships on the board"""
        if player in self.player_objs:
            target_obj = self.player_objs[self.player_targets[player]]

            if len(target_obj.ships_pos) == 0:
                if self.get_name(target_obj) != "AIPlayer":
                    for pos in target_obj.attack_piece_pos:
                        target_obj.attack_piece_pos[pos].setEnabled(False)

                self.disabled_player_obj = target_obj

                self.player_objs.pop(self.player_targets[player],)
                self.player_targets.pop(self.player_targets[player],)

                if len(self.player_objs) > 1:
                    self.next_target(player)
                else:
                    self.close()

    def exec_attack(self, pos, player):
        """Launches an attack on a position picked by a player"""
        if len(self.player_objs) > 1 and player in self.player_objs:
            target_obj = self.player_objs[self.player_targets[player]]
            player_obj = self.player_objs[player]

            if pos in player_obj.attack_piece_pos and pos in target_obj.ships_pos:
                text = player_obj.attack_piece_pos[pos].text()

                target_obj.stored_hit_positions[pos] = 1
                target_obj.ships_pos.pop(pos,)

                if self.get_name(player_obj) != "AIPlayer" and text != '\u25FB':
                    player_obj.attack_piece_pos[pos].setEnabled(False)
                    player_obj.attack_piece_pos[pos].setText('\u25FC')

                self.is_player_target_alive(player)
                
                return 1

            elif pos in player_obj.attack_piece_pos:
                text = player_obj.attack_piece_pos[pos].text()
                target_obj.stored_hit_positions[pos] = 0

                if self.get_name(player_obj) != "AIPlayer" and text not in ('\u25FC', '\u25A3'):
                    player_obj.attack_piece_pos[pos].setText('\u25FB')

                return 0

    def exec_scout(self, pos, player):
        """Launches a scout to see if there is anything in a position picked by a player"""
        if len(self.player_objs) > 1 and player in self.player_objs:
            target_obj = self.player_objs[self.player_targets[player]]
            player_obj = self.player_objs[player]

            if pos in player_obj.attack_piece_pos and pos in target_obj.ships_pos:
                text = player_obj.attack_piece_pos[pos].text()
                target_obj.stored_hit_positions[pos] = 2

                if self.get_name(player_obj) != "AIPlayer" and text != '\u25FB':
                    player_obj.attack_piece_pos[pos].setText('\u25A3')

                return 2

            elif pos in player_obj.attack_piece_pos:
                text = player_obj.attack_piece_pos[pos].text()
                target_obj.stored_hit_positions[pos] = 0

                if self.get_name(player_obj) != "AIPlayer" and text not in ('\u25FC', '\u25A3'):
                    player_obj.attack_piece_pos[pos].setText('\u25FB')

                return 0

    def exec_events(self, player):
        """Executes all events stored by a player, deletes an event if there are no remaining
        positions for the event"""
        if len(self.player_objs) > 1 and player in self.player_objs:
            target_ships_pos = self.player_objs[self.player_targets[player]].ships_pos
            player_obj = self.player_objs[player]

            events = {**player_obj.stored_events}

            def exec_event(event, event_id, pos):
                if pos in player_obj.attack_piece_pos:
                    if event.event_type == "Attack":
                        self.exec_attack(pos, player)

                        if pos in target_ships_pos:
                            player_obj.stored_events.pop(event_id,)
                    else:
                        self.exec_scout(pos, player)
                    event.last_pos = pos
                
                else:
                    player_obj.stored_events.pop(event_id,)
                    return False
                return True

            for event_id in events:
                event = events[event_id]

                if event.last_pos != None:
                    for _ in range(0, event.distance):
                        if event.orientation == "N":
                            pos = (event.last_pos[0]+1, event.last_pos[1])
                        elif event.orientation == "W":
                            pos = (event.last_pos[0], event.last_pos[1]+1)
                        elif event.orientation == "S":
                            pos = (event.last_pos[0]-1, event.last_pos[1])
                        else:
                            pos = (event.last_pos[0], event.last_pos[1]-1)

                        if not exec_event(event, event_id, pos):
                            del event
                            break

                else:
                    for dist in range(0, event.distance):
                        if event.orientation == "N":
                            pos = (dist, event.pos[1])
                        elif event.orientation == "W":
                            pos = (event.pos[0], dist)
                        elif event.orientation == "S":
                            pos = (player_obj.board_size[0]-dist+1, event.pos[1])
                        else:
                            pos = (event.pos[0], player_obj.board_size[1]-dist+1)

                        if not exec_event(event, event_id, pos):
                            del event
                            break

            gc.collect()

    def quit(self, player):
        """Let's a player quit the game, by deleting the player from the manager"""
        player_obj = self.player_objs[player]

        if player in self.player_objs:
            for player_id in self.player_targets:
                if self.player_targets[player_id] == player:
                    hunter = player_id

            if self.windows and self.get_name(player_obj) != 'AIPlayer':
                self.windows[player].close()

            self.disabled_player_obj = player_obj

            self.player_objs.pop(player,)
            self.player_targets.pop(player,)

            if len(self.player_objs) > 1:
                self.next_target(hunter)
            else:
                self.close()

    def reset(self, player_amount, player_objs, windows=None):
        """Resets the manager to accept new players"""
        self.disabled_player_obj = None
        self.player_objs.clear()
        self.player_targets.clear()

        if self.windows:
            self.windows.clear()

        self.gen_players(player_amount, player_objs)
        self.windows = windows

    def show(self):
        """Shows all the stored player attack windows"""
        if self.windows != None:
            for win in self.windows.values():
                win.show()

        self.check_widgets()
        return None

    def close(self):
        """Closes all the stored player attack windows and executes the given 
        closing function"""
        if self.windows != None:
            for win in self.windows.values():
                win.close()

        if self.close_func != None:
            self.close_func()
        return None

class ShipManager:
    """Manages the type of ships that are going to be used in the game"""
    def __init__(self, directory=None):
        self.selected_ships = None
        self.stored_ships = {
            'default': {
                    'patrol_boat': PatrolBoat(),
                    'destroyer': Destroyer(),
                    'submarine': Submarine(),
                    'battle_ship': BattleShip(),
                    'aircraft_carrier': AircraftCarrier()
                }
            }

        if directory:
            self.import_ships(directory)
        self.set_ships('default')

    def set_ships(self, ships_name):
        """Sets the type of ships that are going to be used in the game"""
        if ships_name in self.stored_ships:
            self.selected_ships = self.stored_ships[ships_name]
        else:
            print(f"KeyError!: Selected ships-{ships_name} does not exist!")

    def import_ships(self, directory):
        """Imports the relevant data from a directory and stores it inside ships"""
        def import_file(file_dir):
            def set_data(name, ship_dat):
                """Sets the extracted data to a ship"""
                for dat in ship_dat:
                    if hasattr(ships[name], dat.lower()):
                        setattr(ships[name], dat, ship_dat[dat])
                    else:
                        print(f"AttributeError!: {name} does not have the attribute {dat}!")

            ships = {'patrol_boat': PatrolBoat(), 'destroyer': Destroyer(), 'submarine': Submarine(), 
                'battle_ship': BattleShip(), 'aircraft_carrier': AircraftCarrier()}

            if file_dir.suffix == ".json":
                with open(file_dir, "r") as f:
                    file_data = json.load(f)

                if file_data.get('name', 'ships'):
                    for ship_name in file_data['ships']:
                        if ship_name in ships:
                            set_data(ship_name, file_data['ships'][ship_name])
                        else:
                            print(f"WARNING!: {ship_name} is an invalid ship name!")

                    self.stored_ships[file_data['name']] = ships

            else:
                print(f"FileNotFoundError: Selected file {file_dir} must be a json file!") # Change to popup

        dir_path = Path(directory)

        if dir_path.is_file():
            import_file(dir_path)

        elif dir_path.is_dir():
            files = [dir_path/f for f in dir_path.iterdir() if Path(dir_path, f).is_file()]

            for f in files:
                import_file(f)

        else:
            print(f"FileNotFoundError: Selected directory-{directory} does not exist!") # Change to popup

def SettingsManager:
    def __init__(self, conf_dir):
        self.settings = {
            "game": {
                "custom_ships": False,
                "max_players": 4,

                "debug_mode": False
            },
            "appearence": {
                "windows_theme": "light",
                "windows_style": "Fusion"
            }
        }

        self.read(conf_dir)

    def strtoboolean(self, str_):
        if str_.lower() in ('', 'false', 'none', 'null'):
            return False
        return True

    def set_settings(self, category, data):
        settings_types = {
            'game': {
                'custom_ships': self.strtoboolean,
                'max_players': int,

                'debug_mode': self.strtoboolean
            },
            'appearence': {
                'windows_theme': str,
                'windows_style': str
            }
        }

        for k in data:
            if k in self.settings[category]:
                if k in settings_types:
                    self.settings[category][k] = settings_types[k](data[k])
                else:
                    self.settings[category][k] = data[k]

            else:
                print(f"KeyError: Invalid {k} settings key!")

    def read(self, directory):
        parser = configparser.ConfigParser()

        try:
            parser.read(directory)
        except:
            print("FileNotFoundError: Failed to read config file!")

        if dict(parser).get("GAME", "APPEARENCE"):
            set_settings('game', parser['GAME'], settings_filter)
            set_settings('appearence', parser['APPEARENCE'], settings_filter)
        else:
            print(("KeyError: Key 'GAME' & 'APPEARENCE' does not exist within "
                "the config file!"))

if __name__ == "__main__":
    sh = ShipManager()
    sh.import_ships("/home/hkaar/Documents/Code/Python/App_Testing/Battle-Ship/examples")
    print(sh.stored_ships)
