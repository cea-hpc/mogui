# -*- coding: utf-8 -*-

# SETUP-ENV.CSH, initialize MoGui in a CSH shell session
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

if ($?tcsh) then
    set _mg_shell='tcsh'
else
    set _mg_shell='csh'
endif

eval "`mogui-setup-env $_mg_shell`"

unset _mg_shell
