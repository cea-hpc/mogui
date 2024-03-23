# -*- coding: utf-8 -*-
"""MOGUI, GUI frontend for Modules"""
# Copyright (C) 2011-2024 Aurelien Cedeyn
# Copyright (C)      2024 Xavier Delaruelle
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

import argparse
import os
import sys
import warnings

from PyQt5.QtWidgets import QApplication

from mogui.modules import Modulecmd
from mogui.utils import print_debug, print_error
from mogui.qtgui import MoGui


def main():
    """MoGui application main entry point"""
    if not os.environ.get("MODULEPATH"):
        warnings.warn("Module search path empty")

    try:
        modules = Modulecmd()
    except (
        EnvironmentError,
        FileNotFoundError,
        PermissionError,
        RuntimeError,
    ) as error:
        print_error(error)
        sys.exit(1)

    # parse command line arguments
    arg_parser = argparse.ArgumentParser(description="MoGui, GUI frontend for Modules")
    arg_parser.add_argument(
        "shell_out",
        nargs="?",
        choices=["sh", "bash", "ksh", "zsh", "csh", "tcsh", "fish"],
        help="shell to produce environment change code to",
    )
    arg_parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true", help="enable debug mode"
    )
    # manually handle --help option to print usage message on stderr
    if "-h" in sys.argv or "--help" in sys.argv:
        arg_parser.print_help(file=sys.stderr)
        sys.exit(0)
    args = arg_parser.parse_args()

    if args.debug:
        print_debug(modules)

    # Init in Qt gui mode
    app = QApplication(sys.argv)
    app.setApplicationName("MoGui")

    gui = MoGui(modules, shell_out=args.shell_out, debug=args.debug)
    gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
