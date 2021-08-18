# Battle Ship // Game Ui Classes
# Developed using Python3 and PySide2

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

import battleship.main_game as main_game
import battleship.ships as ships

import ui.main_widgets as ui_widgets

from PySide2.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QSizePolicy, QPushButton, QLCDNumber
from PySide2.QtCore import QTimer, Qt

class Ships:
    aircraft_carrier = ships.Aircraft_Carrier()
    battle_ship = ships.Battle_Ship()
    submarine = ships.Submarine()
    destroyer = ships.Destroyer()
    patrol_boat = ships.Patrol_Boat()

class Game_Manager:
    def __init__(self, closing_method=None, theme_manager=None):
        self.closing_method = closing_method
        self.theme_manager = theme_manager

        self.player_objects = {}

    def create(self, player_amount, ai_player_amount, board_size=(7, 7), enable_abilities=False):
        def gen_player_id():
            for gen_id in range(1, 999):
                if gen_id not in self.player_objects:
                    return gen_id
            return None

        def gen_player_windows():
            deploy_windows = []
            attack_windows = []

            for player_id in self.player_objects:
                if isinstance(self.player_objects[player_id], main_game.Player):
                    deploy_window = Deploy_Window(player_id, self.player_objects[player_id], self.deploy_manager, board_size)
                    attack_window = Attack_Window(player_id, self.player_objects[player_id], self.attack_manager, board_size)

                    if self.theme_manager != None:
                        deploy_window.set_window_theme(self.theme_manager)
                        attack_window.set_window_theme(self.theme_manager)

                    deploy_windows.append(deploy_window)
                    attack_windows.append(attack_window)

            self.deploy_manager.player_windows = tuple(deploy_windows)
            self.attack_manager.player_windows = tuple(attack_windows)

        def gen_players():
            for _ in range(0, player_amount):
                player = main_game.Player(1, 1, {})
                self.player_objects[gen_player_id()] = player

            for _ in range(0, ai_player_amount):
                ai_player = main_game.AI_Player(1, 1)
                self.player_objects[gen_player_id()] = ai_player

        if board_size >= (7, 7):
            gen_players()

            self.attack_manager = main_game.Attack_Manager(len(self.player_objects), tuple(self.player_objects.values()), 
                close_method=self.closing_method, enable_abilities=enable_abilities)
            self.deploy_manager = main_game.Deploy_Manager(len(self.player_objects), tuple(self.player_objects.values()),
                self.attack_manager)

            gen_player_windows()
            self.deploy_manager.show()
        else:
            raise ValueError('Entered board size must be 7 x 7 or bigger!')

    def reset(self):
        del self.attack_manager
        del self.deploy_manager
        
        self.player_objects.clear()

class Deploy_Window(QDialog):
    def __init__(self, selected_player, player_object, deploy_manager, board_size=(7, 7)):
        super(Deploy_Window, self).__init__()
        self.deploy_manager = deploy_manager
        self.player_object = player_object

        self.selected_player = selected_player
        self.board_size = board_size

        self._init_window()

    def _init_window(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowTitle(f'Deployment Phase - {self.selected_player}')

        self.setGeometry(0, 0, 920, 640)

        self.set_window_components()
        self.set_window_layout()

    def set_window_components(self):
        self.board = ui_widgets.Deploy_Board(self.board_size[0], self.board_size[1], 
            self.selected_player, self.player_object, self.deploy_manager)

        self.undo_btn = QPushButton('Undo')
        self.undo_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.undo_btn.clicked.connect(lambda: self.deploy_manager.undo_ship_deployment(self.selected_player))

        self.redo_btn = QPushButton('Redo')
        self.redo_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.redo_btn.clicked.connect(lambda: self.deploy_manager.redo_ship_deployment(self.selected_player))

        self.orientation_N_btn = ui_widgets.Orientation_Button('N', self.player_object)
        self.orientation_W_btn = ui_widgets.Orientation_Button('W', self.player_object)
        self.orientation_S_btn = ui_widgets.Orientation_Button('S', self.player_object)
        self.orientation_E_btn = ui_widgets.Orientation_Button('E', self.player_object)

        self.aircraft_carrier_widget = ui_widgets.Deploy_Widget(Ships.aircraft_carrier, self.player_object)
        self.battle_ship_widget = ui_widgets.Deploy_Widget(Ships.battle_ship, self.player_object)
        self.submarine_widget = ui_widgets.Deploy_Widget(Ships.submarine, self.player_object)
        self.destroyer_widget = ui_widgets.Deploy_Widget(Ships.destroyer, self.player_object)
        self.patrol_boat_widget = ui_widgets.Deploy_Widget(Ships.patrol_boat, self.player_object)

        self.finish_btn = QPushButton('Finish')
        self.finish_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.finish_btn.clicked.connect(self.finish_deployment)

    def set_window_layout(self):
        self.window_layout = QVBoxLayout()

        self.topwidget_layout = QHBoxLayout()

        self.topwidget_layout.addWidget(self.undo_btn)
        self.topwidget_layout.addWidget(self.redo_btn)
        self.topwidget_layout.addWidget(self.orientation_N_btn)
        self.topwidget_layout.addWidget(self.orientation_W_btn)
        self.topwidget_layout.addWidget(self.orientation_S_btn)
        self.topwidget_layout.addWidget(self.orientation_E_btn)
        self.topwidget_layout.addWidget(self.finish_btn)

        self.ship_widget_layout = QVBoxLayout()

        self.ship_widget_layout.addWidget(self.aircraft_carrier_widget)
        self.ship_widget_layout.addWidget(self.battle_ship_widget)
        self.ship_widget_layout.addWidget(self.submarine_widget)
        self.ship_widget_layout.addWidget(self.destroyer_widget)
        self.ship_widget_layout.addWidget(self.patrol_boat_widget)

        self.ship_widget_dialog = QDialog()

        self.ship_widget_dialog.setLayout(self.ship_widget_layout)
        self.ship_widget_dialog.setMaximumWidth(425)
        self.ship_widget_dialog.setMinimumWidth(225)

        self.main_widget_layout = QHBoxLayout()

        self.main_widget_layout.addWidget(self.ship_widget_dialog)
        self.main_widget_layout.addWidget(self.board)

        self.window_layout.addLayout(self.topwidget_layout)
        self.window_layout.addLayout(self.main_widget_layout)

        self.setLayout(self.window_layout)

    def set_window_theme(self, theme_manager):
        theme_manager.set_widget_theme(self)
        theme_manager.set_widget_theme(self.ship_widget_dialog, 'embeded window')
        theme_manager.set_widget_theme((
            self.aircraft_carrier_widget,
            self.battle_ship_widget,
            self.submarine_widget,
            self.destroyer_widget,
            self.patrol_boat_widget,
            self.finish_btn
            ),
        'button')

    def finish_deployment(self):
        self.deploy_manager.finish_player_deployment(self.selected_player)
        self.finish_btn.setEnabled(False)

class Attack_Window(QDialog):
    def __init__(self, selected_player, player_object, attack_manager, board_size=(7, 7)):
        super(Attack_Window, self).__init__()
        self.attack_manager = attack_manager
        self.player_object = player_object

        self.selected_player = selected_player
        self.board_size = board_size

        self._init_window()

    def _init_window(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowTitle(f'Attack Phase - {self.selected_player}')

        self.setGeometry(0, 0, 920, 640)

        self.set_window_components()
        self.set_window_layout()

        self.set_update_timer()

    def set_window_components(self):
        self.board = ui_widgets.Attack_Board(self.board_size[0], self.board_size[1], 
            self.selected_player, self.player_object, self.attack_manager)

        if self.attack_manager.enable_abilities:
            self.default_attack_btn = QPushButton('Attack')
            self.default_attack_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.default_attack_btn.clicked.connect(lambda: self.default_button_method('A'))

            self.default_scout_btn = QPushButton('Scout')
            self.default_scout_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.default_scout_btn.clicked.connect(lambda: self.default_button_method('S'))

            self.points_display = ui_widgets.Points_Display()
            self.points_display.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

            self.orientation_N_btn = ui_widgets.Orientation_Button('N', self.player_object)
            self.orientation_W_btn = ui_widgets.Orientation_Button('W', self.player_object)
            self.orientation_S_btn = ui_widgets.Orientation_Button('S', self.player_object)
            self.orientation_E_btn = ui_widgets.Orientation_Button('E', self.player_object)

            self.finish_btn = QPushButton('Finish')
            self.finish_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.finish_btn.clicked.connect(lambda: self.attack_manager.next_turn(self.selected_player))
        else:
            self.player_object.selected_ship = None

        self.current_turn_display = QLCDNumber(2)
        self.current_turn_display.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        if self.attack_manager.enable_abilities:
            self.aircraft_carrier_widget = ui_widgets.Attack_Widget(Ships.aircraft_carrier, self.player_object, False)
            self.battle_ship_widget = ui_widgets.Attack_Widget(Ships.battle_ship, self.player_object, False)
            self.submarine_widget = ui_widgets.Attack_Widget(Ships.submarine, self.player_object, False)
            self.destroyer_widget = ui_widgets.Attack_Widget(Ships.destroyer, self.player_object, False)
            self.patrol_boat_widget = ui_widgets.Attack_Widget(Ships.patrol_boat, self.player_object, False)
        else:
            self.aircraft_carrier_widget = ui_widgets.Attack_Widget(Ships.aircraft_carrier, self.player_object)
            self.battle_ship_widget = ui_widgets.Attack_Widget(Ships.battle_ship, self.player_object)
            self.submarine_widget = ui_widgets.Attack_Widget(Ships.submarine, self.player_object)
            self.destroyer_widget = ui_widgets.Attack_Widget(Ships.destroyer, self.player_object)
            self.patrol_boat_widget = ui_widgets.Attack_Widget(Ships.patrol_boat, self.player_object)

    def set_window_layout(self):
        self.window_layout = QVBoxLayout()

        if self.attack_manager.enable_abilities:
            self.topwidget_layout = QHBoxLayout()

            self.topwidget_layout.addWidget(self.default_attack_btn)
            self.topwidget_layout.addWidget(self.default_scout_btn)
            self.topwidget_layout.addWidget(self.orientation_N_btn)
            self.topwidget_layout.addWidget(self.orientation_W_btn)
            self.topwidget_layout.addWidget(self.orientation_S_btn)
            self.topwidget_layout.addWidget(self.orientation_E_btn)

            self.topwidget_layout.addWidget(self.current_turn_display)
            self.topwidget_layout.addWidget(self.finish_btn)

        self.ship_widget_layout = QVBoxLayout()

        self.ship_widget_layout.addWidget(self.aircraft_carrier_widget)
        self.ship_widget_layout.addWidget(self.battle_ship_widget)
        self.ship_widget_layout.addWidget(self.submarine_widget)
        self.ship_widget_layout.addWidget(self.destroyer_widget)
        self.ship_widget_layout.addWidget(self.patrol_boat_widget)

        self.ship_widget_dialog = QDialog()

        self.ship_widget_dialog.setLayout(self.ship_widget_layout)
        self.ship_widget_dialog.setMaximumWidth(425)
        self.ship_widget_dialog.setMinimumWidth(225)

        if self.attack_manager.enable_abilities:
            self.widget_layout = QVBoxLayout()

            self.widget_layout.addWidget(self.points_display)
            self.widget_layout.addWidget(self.board)

            self.main_widget_layout = QHBoxLayout()

            self.main_widget_layout.addWidget(self.ship_widget_dialog)
            self.main_widget_layout.addLayout(self.widget_layout)

            self.window_layout.addLayout(self.topwidget_layout)
        else:
            self.widget_layout = QVBoxLayout()

            self.widget_layout.addWidget(self.current_turn_display)
            self.widget_layout.addWidget(self.board)

            self.main_widget_layout = QHBoxLayout()

            self.main_widget_layout.addWidget(self.ship_widget_dialog)
            self.main_widget_layout.addLayout(self.widget_layout)

        self.window_layout.addLayout(self.main_widget_layout)
        
        self.setLayout(self.window_layout)

    def set_window_theme(self, theme_manager):
        theme_manager.set_widget_theme(self)
        theme_manager.set_widget_theme(self.ship_widget_dialog, 'embeded window')
        theme_manager.set_widget_theme((
            self.aircraft_carrier_widget,
            self.battle_ship_widget,
            self.submarine_widget,
            self.destroyer_widget,
            self.patrol_boat_widget
            ),
        'button')

    def set_update_timer(self):
        def update_method():
            if self.attack_manager.enable_abilities:
                self.points_display.display(self.player_object.attack_points, self.player_object.scout_points)
            self.current_turn_display.display(self.attack_manager.current_active_turn)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(update_method)
        self.update_timer.start(125)

    def default_button_method(self, mode):
        self.player_object.selected_ship = None
        self.player_object.current_mode = mode
