# -*- coding: utf-8 -*-
"""MOGUI.UTILS, misc utility functions"""
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

import sys


def print_debug(message):
    """Print message with debug prefix on stderr"""
    print(f"[DEBUG] {message}", file=sys.stderr)


def print_error(message):
    """Print message with error prefix on stderr"""
    print(f"ERROR: {message}", file=sys.stderr)
