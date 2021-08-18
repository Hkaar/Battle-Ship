# Battle Ship // Main
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

import ui.main_ui as main_ui
import sys

from PySide2.QtWidgets import QApplication, QStyleFactory

def main():
    App = QApplication(sys.argv)
    App.setStyle(QStyleFactory.create("Fusion"))

    menu = main_ui.Main_Menu()

    sys.exit(App.exec_())

if __name__ == "__main__":
    main()
