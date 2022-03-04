# Battle Ship // __init__

__copyright__ = "Copyright (C) 2021-2022 Hkaar. All rights reserved."
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

__author__ = "Hkaar"
__version__ = "0.1.1"

#import ui.windows as windows # Disable for testing

#from battleship import managers, players
import managers, players # Temporary import for testing

try:
    import ui_manager as uim
    installed = True
except:
    installed = False

class GameManager:
    """A Manager to create matches and manage the attack and deploy managerds"""
    def __init__(self, close_func=None, directory=None, theme_manager=None):
        self.get_name = lambda obj: obj.__class__.__name__

        self.close_func = close_func
        self.directory = directory
        self.theme_manager = theme_manager

        self.attack_manager = None
        self.deploy_manager = None

        self.player_objs = {}

    def create_game(self, p_amount=2, ai_amount=0, abilities=False, board_size=(7, 7)):
        """A function to create a game match and set some settings for the game match"""
        def gen_id():
            """A function to generates player ids"""
            for player_id in range(0, 999):
                if player_id not in self.player_objs:
                    return player_id
            return None

        def gen_wins():
            """Generates the deploy and attack windows for each non-AI player"""
            deploy_wins = []
            attack_wins = []

            for player_id in self.player_objs:
                if self.get_name(self.player_objs[player_id]) == "Player":
                    deploy_win = windows.DeployWindow(player_id, self.player_objs[player_id], 
                        self.deploy_manager, board_size)
                    attack_win = windows.AttackWindow(player_id, self.player_objs[player_id], 
                        self.attack_manager, board_size)

                    if self.theme_manager:
                        self.theme_manager.set_widget_theme((deploy_win, attack_win))

                    deploy_wins.append(deploy_win)
                    attack_wins.append(attack_win)

            self.deploy_manager.player_windows = tuple(deploy_windows)
            self.attack_manager.player_windows = tuple(attack_windows)

        def gen_players():
            """Generates the player and AI player objects based on player amount"""
            for _ in range(0, p_amount):
                ship_manager = managers.ShipManager(self.directory)
                self.player_objs[gen_id()] = players.Player(ship_manager)

            for _ in range(0, ai_amount):
                ship_manager = managers.ShipManager(self.directory)
                self.player_objs[gen_id()] = players.AIPlayer(ship_manager, board_size)
            return None

        if board_size >= (7, 7):
            gen_players()

            player_amount = len(self.player_objs) 
            player_objs = tuple(self.player_objs.values())

            if not self.attack_manager and not self.deploy_manager:
                self.attack_manager = managers.AttackManager(player_amount, player_objs,
                    close_func=self.close, enable_abilities=abilities)
                self.deploy_manager = managers.DeployManager(player_amount, player_objs,
                    self.attack_manager)
            else:
                self.attack_manager.reset(player_amount, player_objs)
                self.deploy_manager.reset(player_amount, player_objs)

            gen_wins()
            self.deploy_manager.show()

        else:
            raise ValueError("Board size for game must be 7 x 7 or bigger!") # Change to pop up

    def close(self):
        """Executes the given close function and to clear the stored player 
        objects"""
        if self.close_func:
            self.close_func()

        self.player_objs.clear()

class MainManager:
    def __init__(self, conf_dir, main_win=None):
        self.main_win = main_win
        self.windows = []

        self.settings_mgr = managers.SettingsManager(conf_dir)
        self.settings = self.settings_mgr.settings

        if installed:
            self.theme_manager = ui_manager.Theme_Manager(
                self.settings['appearence']['windows_theme'])
        else:
            self.theme_manager = None

        self.game_mgr = GameManager(theme_manager=self.theme_manager)
        self.reload()

    def reload(self):
        if self.main_win and self.main_win not in self.windows:
            self.windows.append(self.main_win)

        self.theme_manager.stored_widgets.clear()
        self.theme_manager.add_widget(self.windows)

        self.theme_manager.load_theme()

if __name__ == "__main__":
    h = MainManager()
    print(h.settings)
