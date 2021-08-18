# Battle Ship // Main Ui
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

import ui.game_ui as game_ui
import ui_manager

import configparser

from PySide2.QtWidgets import QDialog, QInputDialog, QShortcut, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea, QToolBox, QComboBox, QPushButton, QLabel
from PySide2.QtGui import QFont, QKeySequence
from PySide2.QtCore import Qt, Slot

parser = configparser.ConfigParser()
parser.read("config.ini")

try:
    game_info = parser["GAME_INFO"]
    appearence = parser["APPEARENCE"]
except KeyError:
    raise ImportError('An Error has occoured!, while importing the config file!')

class Main_Menu(QDialog):
    def __init__(self, *args, **kwargs):
        super(Main_Menu, self).__init__(*args, **kwargs)
        self.stored_windows = [self]
        self._init_menu()

    def _init_menu(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Main Menu')

        self.setGeometry(0, 0, 640, 480)
        self.setMaximumSize(640, 480)

        self.set_menu_components()
        self.set_menu_layout()

        self.set_menu_theme()

        self.show()

    def set_menu_components(self):
        self.title = QLabel('BATTLE\n SHIP')
        self.title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.title.setFont(QFont("Cantarell ", 35))
        self.title.setMaximumHeight(200)

        self.title_image = QLabel()
        self.title_image.setMaximumSize(387, 458)

        self.start = QPushButton('Start')
        self.start.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.start.clicked.connect(self.show_start_menu)

        self.settings = QPushButton('Settings')
        self.settings.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.settings.clicked.connect(self.show_settings_menu)

        self.help = QPushButton('Help')
        self.help.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.help.clicked.connect(self.show_help_win)

        self.quit = QPushButton('Quit')
        self.quit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.quit.clicked.connect(self.quit_game)

    def set_menu_layout(self):
        self.menu_layout = QHBoxLayout()

        self.title_widgets_layout = QVBoxLayout()

        self.title_widgets_layout.addWidget(self.title)
        self.title_widgets_layout.addWidget(self.start)
        self.title_widgets_layout.addWidget(self.settings)
        self.title_widgets_layout.addWidget(self.help)
        self.title_widgets_layout.addWidget(self.quit)

        self.title_widgets_dialog = QDialog()

        self.title_widgets_dialog.setLayout(self.title_widgets_layout)
        self.title_widgets_dialog.setMaximumWidth(225)

        self.menu_layout.addWidget(self.title_image)
        self.menu_layout.addWidget(self.title_widgets_dialog)

        self.setLayout(self.menu_layout)

    def set_menu_theme(self):
        self.theme_manager = ui_manager.QThemeManager(appearence['STARTUP_THEME'])

        self.theme_manager.set_widget_theme(self)
        self.theme_manager.add_widget(self)

        self.theme_manager.set_widget_theme(self.title_widgets_dialog, 'embeded window')
        self.theme_manager.add_widget(self.title_widgets_dialog, 'embeded window')

    def show_start_menu(self):
        if not hasattr(self, 'start_menu'):
            self.start_menu = Start_Menu(self)

            self.theme_manager.set_widget_theme(self.start_menu)
            self.theme_manager.add_widget(self.start_menu)

            self.stored_windows.append(self.start_menu)
        self.start_menu.show()

    def show_settings_menu(self):
        if not hasattr(self, 'settings_menu'):
            self.settings_menu = Settings_Menu(self)

            self.theme_manager.set_widget_theme(self.settings_menu)
            self.theme_manager.add_widget(self.settings_menu)

            self.stored_windows.append(self.settings_menu)
        self.settings_menu.show()

    def show_help_win(self):
        if not hasattr(self, 'help_win'):
            self.help_win = Help_Window()

            self.theme_manager.set_widget_theme(self.help_win)
            self.theme_manager.add_widget(self.help_win)

            self.stored_windows.append(self.help_win)
        self.help_win.show()

    def quit_game(self):
        for win in self.stored_windows:
            win.close()
        return None

class Start_Menu(QDialog):
    def __init__(self, parent_menu=None, *args, **kwargs):
        super(Start_Menu, self).__init__(*args, **kwargs)
        self.special_mode_status = False
        self.current_board_size = (7, 7)
        self.parent_menu = parent_menu
        self._init_window()

    def _init_window(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Start')

        self.setGeometry(0, 0, 360, 480)
        self.setMaximumSize(640, 920)

        self.set_menu_components()
        self.set_menu_layout()

    def set_menu_components(self):
        self.title = QLabel('BATTLE SHIP')
        self.title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.title.setFont(QFont("Cantarell ", 40))
        self.title.setMaximumHeight(200)

        self.special_mode_switch = QPushButton('Special mode: Disabled')
        self.special_mode_switch.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.special_mode_switch.clicked.connect(self.change_special_mode_status)

        self.board_size_selector = QPushButton(f'Current board size: {self.current_board_size[0]}x{self.current_board_size[1]}')
        self.board_size_selector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.board_size_selector.clicked.connect(self.change_board_size)

        self.start_game_2P = QPushButton("VS 2 Player")
        self.start_game_2P.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.start_game_2P.clicked.connect(lambda: self.create_game(2, 0))

        self.start_game_4P = QPushButton("VS 4 Player")
        self.start_game_4P.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.start_game_4P.clicked.connect(lambda: self.create_game(4, 0))

        self.start_game_2AI = QPushButton("VS 2 AI")
        self.start_game_2AI.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.start_game_2AI.clicked.connect(lambda: self.create_game(1, 1))

        self.start_game_4AI = QPushButton("VS 4 AI")
        self.start_game_4AI.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.start_game_4AI.clicked.connect(lambda: self.create_game(1, 3))

    def set_menu_layout(self):
        self.menu_layout = QVBoxLayout()

        self.special_buttons_layout = QHBoxLayout()

        self.special_buttons_layout.addWidget(self.special_mode_switch)
        self.special_buttons_layout.addWidget(self.board_size_selector)

        self.menu_layout.addWidget(self.title)
        self.menu_layout.addLayout(self.special_buttons_layout)
        self.menu_layout.addWidget(self.start_game_2P)
        self.menu_layout.addWidget(self.start_game_4P)
        self.menu_layout.addWidget(self.start_game_2AI)
        self.menu_layout.addWidget(self.start_game_4AI)

        self.setLayout(self.menu_layout)

    def create_game(self, player_amount, AI_player_amount):
        if not hasattr(self, 'game_manager'):
            self.game_manager = game_ui.Game_Manager(self.closing_method, self.parent_menu.theme_manager)
        self.game_manager.create(player_amount, AI_player_amount, self.current_board_size, self.special_mode_status)

        for win in self.parent_menu.stored_windows:
            win.close()

    def change_special_mode_status(self):
        if self.special_mode_status:
            self.special_mode_switch.setText('Special mode: Disabled')
            self.special_mode_status = False
        else:
            self.special_mode_switch.setText('Special mode: Enabled')
            self.special_mode_status = True

    def change_board_size(self):
        board_y, y_validity = QInputDialog.getInt(self, 'Change Board Size', 'Enter board Y size:')
        board_x, x_validity = QInputDialog.getInt(self, 'Change Board Size', 'Enter board X size:')
        board_size = (board_y, board_x)

        if (y_validity and x_validity) and board_size >= (7, 7):
            self.current_board_size = board_size
        self.board_size_selector.setText(f'Current board size: {self.current_board_size[0]}x{self.current_board_size[1]}')

    def closing_method(self):
        self.game_manager.reset()
        self.parent_menu.show()

class Settings_Menu(QDialog):
    def __init__(self, parent_menu=None, *args, **kwargs):
        super(Settings_Menu, self).__init__(*args, **kwargs)
        self.parent_menu = parent_menu
        self._init_window()

    def _init_window(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Settings')

        self.setGeometry(0, 0, 640, 480)
        self.setMaximumSize(640, 480)

        self.set_menu_components()
        self.set_menu_layout()

    def set_menu_components(self):
        self.settings_seperator = QToolBox()

        self.appearence_layout = QVBoxLayout()
        self.appearence_layout.setAlignment(Qt.AlignTop)

        self.appearence_select_theme = QComboBox()
        self.appearence_select_theme.addItems(self.parent_menu.theme_manager.stored_themes.keys())
        self.appearence_select_theme.activated.connect(self.change_theme)

        self.appearence_layout.addWidget(self.appearence_select_theme)

        self.appearence_tab = QDialog()
        self.appearence_tab.setLayout(self.appearence_layout)

        self.settings_seperator.addItem(self.appearence_tab, 'Appearence')

        self.reload_shortcut = QShortcut(QKeySequence("F5"), self)
        self.reload_shortcut.activated.connect(self.reload_win_content)

    def set_menu_layout(self):
        self.menu_layout = QHBoxLayout()

        self.menu_layout.addWidget(self.settings_seperator)

        self.setLayout(self.menu_layout)

    def change_theme(self, theme_index):
        theme = self.appearence_select_theme.itemText(theme_index)

        if theme in self.parent_menu.theme_manager.stored_themes:
            self.parent_menu.theme_manager.set_theme(theme)
        
        self.parent_menu.theme_manager.load_theme()
        appearence['STARTUP_THEME'] = theme

        with open("config.ini", 'w') as cfg:
            parser.write(cfg)

    @Slot()
    def reload_win_content(self):
        self.appearence_select_theme.clear()
        self.appearence_select_theme.addItems(self.parent_menu.theme_manager.stored_themes.keys())

class Help_Window(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(Help_Window, self).__init__(*args, **kwargs)
        self._init_window()

    def _init_window(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Help')

        self.setGeometry(0, 0, 640, 480)
        self.setMaximumSize(640, 480)

        self.set_window_components()

    def set_window_components(self):
        self.help_content = (
            'Welcome to Battle Ship!\n'
            f'Version: {game_info["version"]}\n'
            '\n'
            'Copyright (c) 2021 Hkaar\n'
            '\n'
            'Battle Ship is distributed under the GNU General Public License (GPL) V3. The\n'
            'program contains a few parts that are distributed under a different license, see\n'
            'LICENSE.txt and LICENSE-3RD-PARTY.txt for full details.\n'
            '\n'
            '-------------------------------------------------------------------\n'
            'Battle Ship is free software: you can redistribute it and/or modify\n'
            'it under the terms of the GNU General Public License as published by\n'
            'the Free Software Foundation, either version 3 of the License, or\n'
            'any later version.\n'
            '\n'
            'Battle Ship is distributed in the hope that it will be useful,\n'
            'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n'
            'GNU General Public License for more details.\n'
            '\n'
            'You should have received a copy of the GNU General Public License\n'
            'along with this program. If not, see <https://www.gnu.org/licenses/>.\n'
            '-------------------------------------------------------------------\n'
            '\n'
            'Battle Ship is a game where you control a fleet of ships and fight against another player\n'
            'or fight against the computer, you control and command your ships attack against the enemy\n'
            'fleet to win the battle.\n'
            '\n'
            'HOW TO PLAY:\n'
            'Deploy Phase:\n'
            '   - Select and deploy your ships.\n'
            '   - Select your ships from the left side panel.\n'
            '   - Adjust the orientation of your ship, with the direction of north,\n'
            '     west, south, east buttons on the top panel.\n'
            '   - Undo or redo deployment of your ship, press the undo or redo button\n'
            '     on the top panel.\n'
            '   - Make sure all your ships are deployed correctly.\n'
            '   - After finish deploying, press the finish button on the top right.\n'
            '\n'
            'Attack Phase (abilities: disabled):\n'
            '   - Select which area of the board you want to attack.\n'
            '   - If the area turns to 0 = Miss, X = Hit.\n'
            '   - Just keep attacking until you destroyed the enemy fleet\n'
            '     or until you lose.\n'
            '\n'
            'Attack Phase (abilities: enabled):\n'
            '   - Select which ship and mode you want to attack with.\n'
            '   - Select your ships from the left side panel, every ship has its\n'
            '     own special abilities and cost that are unique to the ship.\n'
            '   - Select which attack from the ship you want to use, with selecting\n'
            '     between the attack and scout buttons.\n'
            '   - If you want to use a default attack, press the attack or scout\n'
            '     buttons on the top panel.\n'
            '   - After selecting your preffered attack method press on which area\n'
            '     of the board you want to attack.\n'
            '   - For Aircraft Carriers (Attack mode) and Patrol Boat (Scout Mode),\n'
            '     you have to select multiple squares to attack.\n'
            '   - If the area has a 0 = Miss, X = Hit, # = Spotted.\n'
            '   - To finish your turn press the finish button, on the top right.\n'
            '\n'
            'Theres nothing down here ;)'
            )

        self.help_display = QLabel(self.help_content)
        self.help_display.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.setWidget(self.help_display)
        self.setWidgetResizable(True)
