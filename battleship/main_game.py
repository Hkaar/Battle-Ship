# Battle Ship // Main Game Classes
# Developed using Python3

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

import threading
import random
import gc

from battleship.ships import Patrol_Boat, Destroyer, Submarine, Battle_Ship, Aircraft_Carrier

class Deploy_Manager:
    def __init__(self, player_amount, player_objects, attack_manager, player_windows=None):
        self.attack_manager = attack_manager
        self.player_windows = player_windows

        self.deployment_status = {}
        self.player_objects = {}

        self.gen_players(player_amount, player_objects)

    def gen_players(self, player_amount, player_objects):
        if player_amount == len(player_objects):
            for gen_id in range(0, player_amount):
                self.player_objects[gen_id+1] = player_objects[gen_id]

                if isinstance(player_objects[gen_id], AI_Player):
                    self.deployment_status[gen_id+1] = True
                else:
                    self.deployment_status[gen_id+1]  = False
        else:
            raise ValueError('Player amount does not match Player objects!')

    def finish_player_deployment(self, selected_player):
        def check_deployment_status():
            for player_id in self.deployment_status:
                if not self.deployment_status[player_id]:
                    return False
            return True

        if selected_player in self.player_objects and not self.deployment_status[selected_player]:
            if len(self.player_objects[selected_player].ship_positions) > 0:
                self.deployment_status[selected_player] = True

                for pos in self.player_objects[selected_player].deploy_piece_positions:
                    self.player_objects[selected_player].deploy_piece_positions[pos].setEnabled(False)

                if check_deployment_status():
                    self.close()
            else:
                return False
        return True

    def undo_ship_deployment(self, selected_player):
        def gen_id():
            for redo_id in range(0, 99):
                if redo_id not in player.redo_positions:
                    return redo_id
            return None

        if selected_player in self.player_objects and not self.deployment_status[selected_player]:
            player = self.player_objects[selected_player]

            if len(player.undo_positions) > 0:
                undo_id = len(player.undo_positions)-1
                redo_id = gen_id()

                if player.undo_selected_ship[undo_id].__class__.__name__ == 'Deploy_Widget':
                    player.undo_selected_ship[undo_id].setEnabled(True)
                player.selected_ship = player.undo_selected_ship[undo_id]

                for pos in player.undo_positions[undo_id]:
                    player.deploy_piece_positions[pos].setText(' ')
                    player.deploy_piece_positions[pos].setEnabled(True)
                    player.ship_positions.pop(pos, None)

                player.redo_selected_ship[redo_id] = player.undo_selected_ship[undo_id]
                player.redo_positions[redo_id] = player.undo_positions[undo_id]

                player.undo_selected_ship.pop(undo_id, None)
                player.undo_positions.pop(undo_id, None)
            else:
                player.undo_selected_ship.clear()
                player.undo_positions.clear()

    def redo_ship_deployment(self, selected_player):
        def gen_id():
            for undo_id in range(0, 99):
                if undo_id not in player.undo_positions:
                    return undo_id
            return None

        if selected_player in self.player_objects and not self.deployment_status[selected_player]:
            player = self.player_objects[selected_player]

            if len(player.redo_positions) > 0:
                redo_id = len(player.redo_positions)-1
                undo_id = gen_id()

                if player.redo_selected_ship[redo_id].__class__.__name__ == 'Deploy_Widget':
                    player.redo_selected_ship[redo_id].setEnabled(False)
                player.selected_ship = None

                for pos in player.redo_positions[redo_id]:
                    player.deploy_piece_positions[pos].setText('[]')
                    player.deploy_piece_positions[pos].setEnabled(False)
                    player.ship_positions[pos] = player.redo_positions[redo_id][pos]

                player.undo_selected_ship[undo_id] = player.redo_selected_ship[redo_id]
                player.undo_positions[undo_id] = player.redo_positions[redo_id]

                player.redo_selected_ship.pop(redo_id, None)
                player.redo_positions.pop(redo_id, None)
            else:
                player.redo_selected_ship.clear()
                player.redo_positions.clear()

    def show(self):
        if self.player_windows != None:
            for win in self.player_windows:
                win.show()
        return None

    def close(self):
        if self.player_windows != None:
            for win in self.player_windows:
                win.close()

        self.attack_manager.show()
        return None

class Attack_Manager:
    def __init__(self, player_amount, player_objects, player_windows=None, close_method=None, enable_abilities=None):
        self.enable_abilities = enable_abilities
        self.close_method = close_method
        self.current_active_turn = 1

        self.player_windows = player_windows
        self.dead_player_object = None

        self.player_objects = {}
        self.player_targets = {}

        self.gen_players(player_amount, player_objects)

    def gen_players(self, player_amount, player_objects):
        if player_amount == len(player_objects):
            for gen_id in range(0, player_amount):
                self.player_objects[gen_id+1] = player_objects[gen_id]

                if isinstance(player_objects[gen_id], AI_Player):
                    player_objects[gen_id].player_id = gen_id+1

                if gen_id+2 <= player_amount:
                    self.player_targets[gen_id+1] = gen_id+2
                else:
                    self.player_targets[gen_id+1] = (gen_id+2)-player_amount
        else:
            raise ValueError("Player amount does not match Player objects!")

    def next_target(self, selected_player):
        def get_next_target():
            targeted_players = tuple(self.player_targets.values())

            for player_id in self.player_targets:
                if player_id not in targeted_players:
                    return player_id
            return None

        def load_hit_positions():
            if self.player_targets.get(selected_player):
                target_hit_positions = self.player_objects[self.player_targets[selected_player]].stored_hit_positions
            else:
                target_hit_positions = self.dead_player_object.stored_hit_positions

            piece_positions = self.player_objects[selected_player].attack_piece_positions
            piece_values = {0: '0', 1: 'X', 2: '#'}

            for pos in piece_positions:
                piece_positions[pos].setText(' ')
                piece_positions[pos].setEnabled(True)

            for pos in target_hit_positions:
                if pos in piece_positions and target_hit_positions[pos] in piece_values:
                    piece_positions[pos].setText(piece_values[target_hit_positions[pos]])

                    if target_hit_positions[pos] == 1:
                        piece_positions[pos].setEnabled(False)

        next_player_target = get_next_target()

        if selected_player in self.player_objects and next_player_target != None and len(self.player_objects) > 1:
            self.player_objects[selected_player].stored_events.clear()
            self.player_targets[selected_player] = next_player_target

            if not isinstance(self.player_objects[selected_player], AI_Player):
                load_hit_positions()

    def next_turn(self, selected_player):
        def get_next_player():
            available_players = tuple(self.player_objects.keys())

            if self.current_active_turn in self.player_objects and not isinstance(self.player_objects[self.current_active_turn], AI_Player):
                self.player_objects[self.current_active_turn].reset_positions()

            for player_id in available_players:
                if player_id == available_players[len(self.player_objects)-1] and self.current_active_turn == player_id:
                    return available_players[0]

                elif player_id > self.current_active_turn:
                    return player_id
            return None

        def goto_next_player():
            while True:
                next_player = get_next_player()

                if next_player != None and len(self.player_objects[next_player].ship_positions) > 0 and len(self.player_objects) > 1:
                    if isinstance(self.player_objects[next_player], AI_Player):
                        self.player_objects[next_player].exec_player(self.player_objects[self.player_targets[next_player]].attack_piece_positions, self)
                        self.current_active_turn = next_player
                    else:
                        self.current_active_turn = next_player
                        break
                elif len(self.player_objects[next_player].ship_positions) <= 0:
                    self.current_active_turn = next_player
                else:
                    break

        if selected_player == self.current_active_turn:
            next_player_thread = threading.Thread(target=goto_next_player, daemon=True)
            next_player_thread.start()
            next_player_thread.join()

            if self.current_active_turn in self.player_objects and self.enable_abilities:
                self.player_objects[self.current_active_turn].attack_points += 3
                self.player_objects[self.current_active_turn].scout_points += 3

                self.exec_events(self.current_active_turn)

            self.check_widgets()

    def check_widgets(self):
        def check_player_widgets(player_object):
            available_ships = set([])

            for pos in player_object.ship_positions:
                if player_object.ship_positions[pos] not in available_ships:
                    available_ships.add(player_object.ship_positions[pos])

            for widget_id in player_object.stored_widgets:
                if player_object.stored_widgets[widget_id].ship_object not in available_ships:
                    player_object.stored_widgets[widget_id].setEnabled(False)
            return None

        for player_id in self.player_objects:
            if not isinstance(self.player_objects[player_id], AI_Player):
                check_player_widgets(self.player_objects[player_id])

    def is_player_target_alive(self, selected_player):
        if selected_player in self.player_objects:
            target = self.player_objects[self.player_targets[selected_player]]

            if len(target.ship_positions) == 0:
                if not isinstance(target, AI_Player):
                    for pos in target.attack_piece_positions:
                        target.attack_piece_positions[pos].setEnabled(False)
                self.dead_player_object = target

                self.player_objects.pop(self.player_targets[selected_player], None)
                self.player_targets.pop(self.player_targets[selected_player], None)

                if len(self.player_objects) > 1:
                    self.next_target(selected_player)
                else:
                    self.close()

    def exec_attack(self, pos, selected_player):
        if selected_player in self.player_objects and len(self.player_objects) > 1:
            target = self.player_objects[self.player_targets[selected_player]]
            player = self.player_objects[selected_player]

            if pos in target.ship_positions and pos in player.attack_piece_positions:
                target.stored_hit_positions[pos] = 1
                target.ship_positions.pop(pos, None)

                if not isinstance(player, AI_Player) and player.attack_piece_positions[pos].text() != '0':
                    player.attack_piece_positions[pos].setEnabled(False)
                    player.attack_piece_positions[pos].setText('X')

                self.is_player_target_alive(selected_player)

            elif pos in player.attack_piece_positions:
                target.stored_hit_positions[pos] = 0

                if not isinstance(player, AI_Player) and player.attack_piece_positions[pos].text() not in ('X', '#'):
                    player.attack_piece_positions[pos].setText('0')

    def exec_scout(self, pos, selected_player):
        if selected_player in self.player_objects and len(self.player_objects) > 1:
            target = self.player_objects[self.player_targets[selected_player]]
            player = self.player_objects[selected_player]

            if pos in target.ship_positions and pos in player.attack_piece_positions:
                target.stored_hit_positions[pos] = 2

                if not isinstance(player, AI_Player) and player.attack_piece_positions[pos].text() != '0':
                    player.attack_piece_positions[pos].setText('#')

            elif pos in player.attack_piece_positions:
                target.stored_hit_positions[pos] = 0

                if not isinstance(player, AI_Player) and player.attack_piece_positions[pos].text() not in ('X', '#'):
                    player.attack_piece_positions[pos].setText('0')

    def exec_events(self, selected_player):
        if selected_player in self.player_objects and len(self.player_objects) > 1:
            target_ship_positions = {**self.player_objects[self.player_targets[selected_player]].ship_positions}
            player = self.player_objects[selected_player]

            temp_stored_events = {**player.stored_events}

            def exec_event(event_id, event, pos):
                if pos in player.attack_piece_positions:
                    if event.__class__.__name__ == 'Event_Attack':
                        self.exec_attack(pos, selected_player)
                        if pos in target_ship_positions:
                            player.stored_events.pop(event_id, None)
                            return False
                    else:
                        self.exec_scout(pos, selected_player)
                    event.last_position = pos
                else:
                    player.stored_events.pop(event_id, None)
                    return False
                return True

            for event_id in temp_stored_events:
                event = temp_stored_events[event_id]

                if event.last_position != None:
                    for _ in range(0, event.move_count):
                        if event.orientation == 'N':
                            pos = ((event.last_position[0]+1, event.last_position[1]))
                        elif event.orientation == 'W':
                            pos = ((event.last_position[0], event.last_position[1]+1))
                        elif event.orientation == 'S':
                            pos = ((event.last_position[0]-1, event.last_position[1]))
                        else:
                            pos = ((event.last_position[0], event.last_position[1]-1))

                        if not exec_event(event_id, event, pos):
                            del event
                            break
                else:
                    for xy in range(0, event.move_count):
                        if event.orientation == 'N':
                            pos = ((xy, event.position[1]))
                        elif event.orientation == 'W':
                            pos = ((event.position[0], xy))
                        elif event.orientation == 'S':
                            pos = ((player.board_size[0]-(xy+1), event.position[1]))
                        else:
                            pos = ((event.position[0], player.board_size[1]-(xy+1)))

                        if not exec_event(event_id, event, pos):
                            del event
                            break
                gc.collect()

    def show(self):
        if self.player_windows != None:
            for win in self.player_windows:
                win.show()
        self.check_widgets()

        return None

    def close(self):
        if self.player_windows != None:
            for win in self.player_windows:
                win.close()

        if self.close_method != None:
            self.close_method()

        return None

class Player:
    def __init__(self, attack_points, scout_points, ship_positions, orientation='W'):
        self.attack_points = attack_points
        self.scout_points = scout_points
        self.selected_ship = None

        self.current_special_ship = None
        self.available_positions = 0

        self.orientation = orientation
        self.current_mode = 'A'

        self.ship_positions = ship_positions
        self.deploy_piece_positions = {}
        self.attack_piece_positions = {}
        self.board_size = None

        self.stored_widgets = {}

        self.undo_selected_ship = {}
        self.redo_selected_ship = {}
        self.undo_positions = {}
        self.redo_positions = {}

        self.stored_positions = set([])
        self.stored_hit_positions = {}
        self.stored_events = {}

    def reset_positions(self):
        self.current_special_ship = None
        self.stored_positions.clear()
        self.available_positions = 0

    def add_widget(self, widget):
        def gen_id():
            for widget_id in range(0, 99):
                if widget_id not in self.stored_widgets:
                    return widget_id
            return None

        self.stored_widgets[gen_id()] = widget

    def add_event(self, event):
        def gen_id():
            for event_id in range(0, 999):
                if event_id not in self.stored_events:
                    return event_id
            return None
            
        self.stored_events[gen_id()] = event

class AI_Player:
    def __init__(self, attack_points, scout_points, board_size=(7, 7)):
        self.attack_points = attack_points
        self.scout_points = scout_points
        self.selected_ship = None

        self.current_mode = 'A'
        self.orientation = 'W'
        self.player_id = None

        self.deploy_piece_positions = tuple([(y, x) for y in range(0, board_size[0]) for x in range(0, board_size[1])])
        self.attack_piece_positions = tuple([(y, x) for y in range(0, board_size[0]) for x in range(0, board_size[1])])
        self.board_size = board_size
        self.ship_positions = {}

        self.stored_positions = set([])
        self.stored_hit_positions = {}
        self.stored_events = {}

        self.check_requirements()
        self.gen_ship_positions()

    def gen_ship_positions(self):
        def generate_positions(pos, selected_ship):
            ship_positions = {}

            def add_ship_pos(selected_pos):
                if selected_pos in self.deploy_piece_positions and selected_pos not in self.ship_positions:
                    ship_positions[selected_pos] = selected_ship

            for size_num in range(0, selected_ship.size):
                if self.orientation == 'N':
                    gen_pos = (pos[0]-size_num, pos[1])
                elif self.orientation == 'W':
                    gen_pos = (pos[0], pos[1]-size_num)
                elif self.orientation == 'S':
                    gen_pos = (pos[0]+size_num, pos[1])
                else:
                    gen_pos = (pos[0], pos[1]+size_num)
                add_ship_pos(gen_pos)

            if len(ship_positions) == selected_ship.size:
                self.ship_positions.update(ship_positions)
            else:
                return False
            return True

        def goto_generate_positions():
            deployable_ships = (Patrol_Boat(), Destroyer(), Submarine(), Battle_Ship(), Aircraft_Carrier())
            ship_index = 0

            while ship_index < 5:
                self.orientation = random.choice(('N', 'W', 'S', 'E'))

                if generate_positions(random.choice(self.deploy_piece_positions), deployable_ships[ship_index]):
                    ship_index += 1

        ship_gen_thread = threading.Thread(target=goto_generate_positions, daemon=True)
        ship_gen_thread.start()

    def exec_player(self, target_piece_positions, attack_manager):
        get_name = lambda selected_object: selected_object.__class__.__name__

        def get_ship():
            available_ships = []

            for pos in self.ship_positions:
                if self.ship_positions[pos] not in available_ships:
                    available_ships.append(self.ship_positions[pos])

            return random.choice(tuple(available_ships))

        def gen_positions(position_count):
            while len(self.stored_positions) < position_count:
                pos = random.choice(target_piece_positions)

                if pos not in self.stored_positions:
                    self.stored_positions.add(pos)

        def exec_multiple_attacks():
            if self.stored_positions != None and get_name(self.stored_positions):
                for pos in self.stored_positions:
                    if self.current_mode == 'A':
                        attack_manager.exec_attack(pos, self.player_id)
                    else:
                        attack_manager.exec_scout(pos, self.player_id)
            self.stored_positions = set([])

        self.orientation = random.choice(('N', 'W', 'S', 'E'))
        self.current_mode = random.choice(('A', 'S'))
        self.selected_ship = get_ship()

        if isinstance(target_piece_positions, dict):
            target_piece_positions = tuple(target_piece_positions.keys())
        else:
            target_piece_positions = tuple(target_piece_positions)

        if attack_manager.enable_abilities:
            if (isinstance(self.selected_ship, Aircraft_Carrier) and self.current_mode == 'A') or (isinstance(self.selected_ship, Patrol_Boat) and self.current_mode == 'S'):
                position_counts = {'Aircraft_Carrier': 9, 'Patrol_Boat': 5}

                gen_position_thread = threading.Thread(target=gen_positions, args=(position_counts[get_name(self.selected_ship)],), daemon=True)
                gen_position_thread.start()
                gen_position_thread.join()
            else:
                if self.current_mode == 'A':
                    self.stored_positions = self.selected_ship.get_attack(random.choice(target_piece_positions), self)
                else:
                    self.stored_positions = self.selected_ship.get_scout(random.choice(target_piece_positions), self)
            attack_manager.exec_events(self.player_id)
            exec_multiple_attacks()
        else:
            attack_manager.exec_attack(random.choice(target_piece_positions), self.player_id, q)

    def add_event(self, event):
        def gen_id():
            for event_id in range(0, 999):
                if event_id not in self.stored_events:
                    return event_id
            return None

        self.stored_events[gen_id()] = event

    def check_requirements(self):
        if self.board_size < (7, 7):
            raise ValueError("AI Player board size must be 7 x 7 or bigger!")
