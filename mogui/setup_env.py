# -*- coding: utf-8 -*-
"""MOGUI.SETUP_ENV, MoGui initialization in shell environment"""
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
import sys


class SetupEnv:  # pylint: disable=too-few-public-methods
    """Generic MoGui shell environment setup class"""

    def __init__(self, shell: str):
        self.shell = shell

    def shell_code(self):
        """Return shell code to define MoGui in environnment"""
        raise NotImplementedError()


class ShSetupEnv(SetupEnv):  # pylint: disable=too-few-public-methods
    """Sh-specific MoGui environment setup class"""

    def shell_code(self):
        code = f'mogui() {{ eval "$(mogui-cmd {self.shell} "$@")"; }}'
        return code


class CshSetupEnv(SetupEnv):  # pylint: disable=too-few-public-methods
    """Csh-specific MoGui environment setup class"""

    def shell_code(self):
        code = f"alias mogui 'eval \"`mogui-cmd {self.shell} \\!*:q`\"' ;"
        return code


class FishSetupEnv(SetupEnv):  # pylint: disable=too-few-public-methods
    """Fish-specific MoGui environment setup class"""

    def shell_code(self):
        code = [
            "function mogui",
            "   eval mogui-cmd fish (string escape -- $argv) | source -",
            "end",
        ]
        return "\n".join(code)


def setup_env():
    """Generate code to initialize MoGui in current shell session"""
    # parse command line arguments
    arg_parser = argparse.ArgumentParser(
        description="Generate code to initialize MoGui in shell"
    )
    arg_parser.add_argument(
        "shell",
        choices=["sh", "bash", "ksh", "zsh", "csh", "tcsh", "fish"],
        help="shell to produce MoGui initialization code to",
    )
    # manually handle --help option to print usage message on stderr
    if "-h" in sys.argv or "--help" in sys.argv:
        arg_parser.print_help(file=sys.stderr)
        sys.exit(0)
    args = arg_parser.parse_args()

    # get setup object for selected shell
    if args.shell in ["sh", "bash", "ksh", "zsh"]:
        setup = ShSetupEnv(args.shell)
    elif args.shell in ["csh", "tcsh"]:
        setup = CshSetupEnv(args.shell)
    else:
        setup = FishSetupEnv(args.shell)

    # output shell code to define MoGui
    print(setup.shell_code())
