# Battle Ship // Main Widget Classes
# Developed using Python3 & PySide2

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

from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QLCDNumber, QPushButton, QLabel
from PySide2.QtCore import Qt

class Deploy_Board(QWidget):
    def __init__(self, row_amount, column_amount, selected_player, player_object, deploy_manager):
        super(Deploy_Board, self).__init__()
        self.deploy_manager = deploy_manager
        self.player_object = player_object

        self.selected_player = selected_player
        self._init_board(row_amount, column_amount)

    def _init_board(self, row_amount, column_amount):
        self.main_board_layout = QGridLayout()
        self.main_board_layout.setSpacing(1)

        self.board_positions = [(y, x) for y in range(0, row_amount) for x in range(0, column_amount)]
        piece_positions = {}

        for pos in self.board_positions:
            board_piece = Deploy_Board_Piece(pos, self.selected_player, self.player_object, self.deploy_manager)
            self.main_board_layout.addWidget(board_piece, *pos)
            piece_positions[pos] = board_piece

        self.player_object.deploy_piece_positions = piece_positions
        self.setLayout(self.main_board_layout)

class Attack_Board(QWidget):
    def __init__(self, row_amount, column_amount, selected_player, player_object, attack_manager):
        super(Attack_Board, self).__init__()
        self.attack_manager = attack_manager
        self.player_object = player_object

        self.player_object.board_size = (row_amount, column_amount)
        self.selected_player = selected_player

        self._init_board(row_amount, column_amount)

    def _init_board(self, row_amount, column_amount):
        self.main_board_layout = QGridLayout()
        self.main_board_layout.setSpacing(1)

        self.board_positions = [(y, x) for y in range(0, row_amount) for x in range(0, column_amount)]
        piece_positions = {}

        for pos in self.board_positions:
            board_piece = Attack_Board_Piece(pos, self.selected_player, self.player_object, self.attack_manager)
            self.main_board_layout.addWidget(board_piece, *pos)
            piece_positions[pos] = board_piece

        self.player_object.attack_piece_positions = piece_positions
        self.setLayout(self.main_board_layout)

class Deploy_Board_Piece(QPushButton):
    def __init__(self, position, selected_player, player_object, deploy_manager):
        super(Deploy_Board_Piece, self).__init__()
        self.deploy_manager = deploy_manager
        self.player_object = player_object

        self.selected_player = selected_player
        self.position = position

        self._init_board_piece()

    def _init_board_piece(self):
        self.setText(' ')
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.clicked.connect(self.board_piece_method)

    def board_piece_method(self):
        def generate_positions():
            ship_positions = {}
            ship_size = 0

            def gen_id():
                for gen_id in range(0, 999):
                    if gen_id not in self.player_object.undo_positions:
                        return gen_id
                return None

            def add_ship_pos(selected_pos):
                if selected_pos in self.player_object.deploy_piece_positions and selected_pos not in self.player_object.ship_positions:
                    if isinstance(self.player_object.selected_ship, Deploy_Widget):
                        ship_positions[pos] = self.player_object.selected_ship.ship_object
                    else:
                        ship_positions[pos] = self.player_object.selected_ship
                else:
                    return False
                return True

            if isinstance(self.player_object.selected_ship, Deploy_Widget):
                ship_size = self.player_object.selected_ship.ship_object.size
            else:
                ship_size = self.player_object.selected_ship.size

            for size_num in range(0, ship_size):
                if self.player_object.orientation == 'N':
                    pos = (self.position[0]-size_num, self.position[1])
                elif self.player_object.orientation == 'W':
                    pos = (self.position[0], self.position[1]-size_num)
                elif self.player_object.orientation == 'S':
                    pos = (self.position[0]+size_num, self.position[1])
                else:
                    pos = (self.position[0], self.position[1]+size_num)

                if not add_ship_pos(pos):
                    return False

            if len(ship_positions) == ship_size:
                undo_id = gen_id()

                if isinstance(self.player_object.selected_ship, Deploy_Widget):
                    self.player_object.selected_ship.setEnabled(False)

                self.player_object.undo_positions[undo_id] = {}
                self.player_object.redo_positions.clear()

                for pos in ship_positions:
                    self.player_object.deploy_piece_positions[pos].setText('[]')
                    self.player_object.deploy_piece_positions[pos].setEnabled(False)
                self.player_object.ship_positions.update(ship_positions)

                self.player_object.undo_selected_ship[undo_id] = self.player_object.selected_ship
                self.player_object.undo_positions[undo_id].update(ship_positions)
                self.player_object.selected_ship = None
            return True

        if not self.deploy_manager.deployment_status[self.selected_player] and self.player_object.selected_ship != None:
            if not generate_positions():
                print('The spot is already taken or is invalid!')

class Attack_Board_Piece(QPushButton):
    def __init__(self, position, selected_player, player_object, attack_manager):
        super(Attack_Board_Piece, self).__init__()
        self.attack_manager = attack_manager
        self.player_object = player_object

        self.selected_player = selected_player
        self.position = position

        self._init_board_piece()

    def _init_board_piece(self):
        self.setText(' ')
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.clicked.connect(self.board_piece_method)

    def board_piece_method(self):
        def exec_board_piece():
            get_name = lambda selected_object: selected_object.__class__.__name__

            if isinstance(self.player_object.selected_ship, Attack_Widget):
                selected_ship = self.player_object.selected_ship.ship_object
            else:
                selected_ship = self.player_object.selected_ship

            if self.attack_manager.enable_abilities:
                if selected_ship != None:
                    if self.player_object.current_mode == 'A':
                        if selected_ship.attack_cost > self.player_object.attack_points:
                            return False
                        else:
                            if get_name(selected_ship) != 'Aircraft_Carrier':
                                self.player_object.attack_points -= selected_ship.attack_cost
                            stored_positions = selected_ship.get_attack(self.position, self.player_object)

                        if stored_positions == True:
                            self.player_object.attack_points -= selected_ship.attack_cost

                            for pos in self.player_object.stored_positions:
                                self.attack_manager.exec_attack(pos, self.selected_player)
                            self.player_object.reset_positions()

                        elif stored_positions != None and get_name(stored_positions):
                            for pos in stored_positions:
                                self.attack_manager.exec_attack(pos, self.selected_player)
                            self.player_object.reset_positions()
                    else:
                        if selected_ship.scout_cost > self.player_object.scout_points:
                            return False
                        else:
                            if get_name(selected_ship) != 'Patrol_Boat':
                                self.player_object.scout_points -= selected_ship.scout_cost
                            stored_positions = selected_ship.get_scout(self.position, self.player_object)

                        if stored_positions == True:
                            self.player_object.scout_points -= selected_ship.scout_cost

                            for pos in self.player_object.stored_positions:
                                self.attack_manager.exec_scout(pos, self.selected_player)
                            self.player_object.reset_positions()

                        elif stored_positions != None and get_name(stored_positions):
                            for pos in stored_positions:
                                self.attack_manager.exec_scout(pos, self.selected_player)
                            self.player_object.reset_positions()
                else:
                    if len(self.player_object.ship_positions) > 0:
                        if self.player_object.current_mode == 'A' and self.player_object.attack_points > 0:
                            self.attack_manager.exec_attack(self.position, self.selected_player)
                            self.player_object.attack_points -= 1

                        elif self.player_object.scout_points > 0:
                            self.attack_manager.exec_scout(self.position, self.selected_player)
                            self.player_object.scout_points -= 1
                        self.player_object.reset_positions()
                    else:
                        return False
            else:
                if len(self.player_object.ship_positions) > 0:
                    self.attack_manager.exec_attack(self.position, self.selected_player)
                    self.attack_manager.next_turn(self.selected_player)
                else:
                    return False
            return True

        if self.attack_manager.current_active_turn == self.selected_player:
            if not exec_board_piece():
                print("You don't have enough points to perform that action!")

class Deploy_Widget(QPushButton):
    def __init__(self, ship_object, player_object):
        super(Deploy_Widget, self).__init__()
        self.player_object = player_object
        self.ship_object = ship_object
        self._init_widget()

    def _init_widget(self):
        self.setText(self.ship_object.name)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.clicked.connect(self.deploy_widget_method)

    def deploy_widget_method(self):
        self.player_object.selected_ship = self

class Attack_Widget(QWidget):
    def __init__(self, ship_object, player_object, hide_buttons=True):
        super(Attack_Widget, self).__init__()
        self.player_object = player_object
        self.hide_buttons = hide_buttons
        self.ship_object = ship_object

        self._init_widget()

    def _init_widget(self):
        self.attack_widget_layout = QVBoxLayout()

        self.name_display = QLabel(self.ship_object.name)
        self.name_display.setStyleSheet('border: 1px outset rgb(80, 80, 80);')
        self.name_display.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.attack_widget_layout.addWidget(self.name_display)

        if not self.hide_buttons:
            self.button_layout = QHBoxLayout()

            self.ship_attack_button = QPushButton("Attack")
            self.ship_attack_button.setSizePolicy(QSizePolicy.Minimum,  QSizePolicy.Minimum)
            self.ship_attack_button.clicked.connect(lambda: self.ship_button_method('A'))

            self.ship_scout_button = QPushButton("Scout")
            self.ship_scout_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.ship_scout_button.clicked.connect(lambda: self.ship_button_method('S'))

            self.button_layout.addWidget(self.ship_attack_button)
            self.button_layout.addWidget(self.ship_scout_button)

            self.attack_widget_layout.addLayout(self.button_layout)

        self.setLayout(self.attack_widget_layout)
        self.player_object.add_widget(self)

    def ship_button_method(self, mode):
        self.player_object.selected_ship = self
        self.player_object.current_mode = mode

    def setEnabled(self, state):
        if not state:
            if not self.hide_buttons:
                self.name_display.setText('No signal!')

                self.ship_attack_button.setText('No signal!')
                self.ship_attack_button.setEnabled(False)

                self.ship_scout_button.setText('No signal!')
                self.ship_scout_button.setEnabled(False)

                self.player_object.selected_ship = None
            else:
                self.name_display.setText('No signal!')
                self.player_object.selected_ship = None
        else:
            if not self.hide_buttons:
                self.name_display.setText(self.ship_object.name)

                self.ship_attack_button.setText('Attack')
                self.ship_attack_button.setEnabled(True)

                self.ship_scout_button.setText('Scout')
                self.ship_scout_button.setEnabled(True)
            else:
                self.name_display.setText(self.ship_object.name)

class Orientation_Button(QPushButton):
    def __init__(self, orientation, player_object):
        super(Orientation_Button, self).__init__()
        self.player_object = player_object
        self.orientation = orientation

        self._init_button()

    def _init_button(self):
        self.setText(self.orientation)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.clicked.connect(self.change_orientation)

    def change_orientation(self):
        self.player_object.orientation = self.orientation

class Points_Display(QWidget):
    def __init__(self):
        super(Points_Display, self).__init__()
        self._init_display()

    def _init_display(self):
        self.display_layout = QHBoxLayout()

        self.attack_label = QLabel('Attack')
        self.attack_label.setStyleSheet('border: 1px outset rgb(80, 80, 80)')
        self.attack_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.scout_label = QLabel('Scout')
        self.scout_label.setStyleSheet('border: 1px outset rgb(80, 80, 80)')
        self.scout_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.attack_point_display = QLCDNumber(3)
        self.scout_point_display = QLCDNumber(3)

        self.attack_display_layout = QVBoxLayout()

        self.attack_display_layout.addWidget(self.attack_label)
        self.attack_display_layout.addWidget(self.attack_point_display)

        self.scout_display_layout = QVBoxLayout()

        self.scout_display_layout.addWidget(self.scout_label)
        self.scout_display_layout.addWidget(self.scout_point_display)

        self.display_layout.addLayout(self.attack_display_layout)
        self.display_layout.addLayout(self.scout_display_layout)

        self.setLayout(self.display_layout)

    def display(self, attack_points=0, scout_points=0):
        self.attack_point_display.display(attack_points)
        self.scout_point_display.display(scout_points)
