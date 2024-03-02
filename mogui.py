#!/usr/bin/python
# -*- coding: utf-8 -*-

# MOGUI, GUI frontend for module
# Copyright (C) 2011-2024 Aurelien Cedeyn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

##########################################################################

# TODO:
# - Add Selected property to the Module class

import argparse
import os
import sys
import warnings

from PyQt5.QtWidgets import QApplication

from lib.module import Modulecmd
from lib.utils import print_debug
from gui.mogui import MoGui


if not os.environ.get("MODULEPATH"):
    warnings.warn("Module search path empty")


if __name__ == "__main__":
    modules = Modulecmd()

    # parse command line arguments
    arg_parser = argparse.ArgumentParser(description="MoGui, GUI frontend for Modules")
    arg_parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true", help="enable debug mode"
    )
    # manually handle --help option to print usage message on stderr
    if "-h" in sys.argv or "--help" in sys.argv:
        arg_parser.print_help(file=sys.stderr)
        sys.exit(0)
    args = arg_parser.parse_args()

    # Init in Qt gui mode
    app = QApplication(sys.argv)
    app.setOrganizationName("cea")
    app.setApplicationName("MoGui")
    app.setOrganizationDomain("cea.fr")

    try:
        qss = os.sep.join([os.environ["HOME"], ".config/MoGui", "mogui.qss"])
        app.setStyleSheet("".join(open(qss).readlines()))
    except IOError:
        pass

    if args.debug:
        print_debug(modules)

    gui = MoGui(modules, debug=args.debug)
    gui.setModules()
    gui.show()

    sys.exit(app.exec_())
