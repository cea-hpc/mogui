# -*- coding: utf-8 -*-

# SETUP-ENV.SH, initialize MoGui in a SH shell session
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

# get current shell name by querying shell variables or looking at parent
# process name
if [ -n "${BASH:-}" ]; then
   if [ "${BASH##*/}" = 'sh' ]; then
      _mg_shell='sh'
   else
      _mg_shell='bash'
   fi
elif [ -n "${ZSH_NAME:-}" ]; then
   _mg_shell=$ZSH_NAME
else
   _mg_shell=$(basename "$(ps -p $$ -ocomm=)")
fi

eval "$(mogui-setup-env "$_mg_shell")"

unset _mg_shell
