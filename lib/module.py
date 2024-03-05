# -*- coding: utf-8 -*-

# LIB/MODULE, Python object interface to module
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

import errno
import os
import sys
from subprocess import Popen, PIPE


def get_modulecmd_path():
    """Get path of module command from environment and test this file is
    executable.

    Returns:
        File pathname of module command
    """
    modulecmd_path = os.environ.get("MODULES_CMD")
    if not modulecmd_path:
        raise EnvironmentError("Environment variable 'MODULES_CMD' not defined")

    if not os.path.isfile(modulecmd_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), modulecmd_path)

    if not (os.access(modulecmd_path, os.R_OK) and os.access(modulecmd_path, os.X_OK)):
        raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), modulecmd_path)

    return modulecmd_path


def get_path_envvar_value_list(envvar, sep=":"):
    """Return list value of a path-like environment variable"""
    if os.environ.get(envvar):
        value_list = os.environ.get(envvar).split(sep)
    else:
        value_list = []
    return value_list


class Modulecmd:
    def __init__(self, shell="python"):
        self.shell = shell
        self.avail_mods = {}
        self.avail_fetched = False
        self.modulecmd = get_modulecmd_path()
        self.cmd_version = None

    def run(self, *arguments, out_shell="python", return_content="err"):
        """Run module command with given arguments to produce code for
        specified output shell.

        Args:
            arguments: module command and its arguments to run
            out_shell: shell code kind module should produce
            return_content: return 'out' or 'err' content

        Returns:
            Content produced by run commands. Either stdout or stderr content
            base on return_content value.
        """
        with Popen(
            [self.modulecmd, out_shell] + list(arguments), stdout=PIPE, stderr=PIPE
        ) as proc:
            out, err = proc.communicate()
        if return_content == "out":
            content = out
            if err.decode():
                print(err.decode(), end="", file=sys.stderr)
        else:
            content = err.decode()
        return content

    def eval(self, *arguments):
        """Evaluate content produced by module command run to update current
        environment.

        Args:
            arguments: module command and its argument to run

        Returns:
            Boolean status of content evaluation
        """
        content = self.run(*arguments, return_content="out")
        global_ns = {}
        exec(content, global_ns)
        _mlstatus = global_ns.get("_mlstatus", True)
        return _mlstatus

    def avail(self):
        """Fetch available modules in enabled module search paths

        Returns:
            Hash table with all Module objects
        """
        if not self.avail_fetched:
            lines = self.run("avail", "--terse", "--output=sym").strip().split("\n")
            for mod in lines:
                mod_split_raw = mod.rsplit("(", 1)
                mod_name = mod_split_raw[0]
                if len(mod_split_raw) > 1:
                    mod_syms = mod_split_raw[1].rstrip(")").split(":")
                else:
                    mod_syms = None
                self.avail_mods[mod_name] = Module(mod_name, mod_syms)
            self.avail_fetched = True

        return self.avail_mods

    def loaded(self):
        """Return list of loaded modules"""
        return get_path_envvar_value_list("LOADEDMODULES")

    def used(self):
        """Return list of enabled modulepaths"""
        return get_path_envvar_value_list("MODULEPATH")

    def version(self):
        """Return version of module command"""
        if self.cmd_version is None:
            version_raw = self.run("--version")
            self.cmd_version = version_raw.split()[2]

        return self.cmd_version

    def __repr__(self):
        loaded_str = ", ".join(self.loaded())
        used_str = ", ".join(self.used())
        info = [
            f"Module command version {self.version()}",
            f"Used modulepaths: {used_str}",
            f"Loaded modules: {loaded_str}",
        ]
        return "\n  ".join(info)


class Module:
    """Module file representation

    Args:
        name: module name and version designation
        symbols: list of symbolic versions attached to module
    """

    def __init__(self, name, symbols=None):
        super().__init__()
        self.name = name
        self.symbols = symbols
        self.whatis = None
        self.help_message = None

    def __repr__(self):
        return self.name

    def desc(self, modulecmd: Modulecmd):
        if self.whatis is None:
            self.whatis = modulecmd.run("whatis", self.name).split(":")[1].strip()
            if not self.whatis:
                self.whatis = self.name
        return self.whatis

    def help(self, modulecmd: Modulecmd):
        if self.help_message is None:
            self.help_message = modulecmd.run("help", self.name)
            if not self.help_message:
                self.help_message = f"No help for {self.name}"
        return self.help_message
