# -*- coding: utf-8 -*-

# LIB/MODULE, Python object interface to module
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

import errno
import os
import sys
from subprocess import Popen, PIPE
from distutils.version import LooseVersion


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


class Modulecmd:
    def __init__(self, shell="python"):
        self.shell = shell
        self.mods = {}
        self.modulecmd = get_modulecmd_path()

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
        lines = self.run("avail", "--terse", "--output=sym").strip().split("\n")
        version = "1.0"

        for mod in lines:
            mod_split_raw = mod.rsplit("/", 1)
            mod_name = mod_split_raw[0]
            if len(mod_split_raw) > 1:
                versions = mod_split_raw[1].rstrip(")").replace("(", ":").split(":")
                version = versions[0]
                default = "default" in versions
            else:
                version = None
                default = False

            if mod_name in self.mods:
                self.mods[mod_name].add_version(version, default)
            else:
                self.mods[mod_name] = Module(
                    mod_name,
                    version,
                    default=default,
                )
        return self.mods

    def test(self):
        """
        Create fake module list
        """
        for i in range(1, 10):
            name = "test%d" % i
            self.mods[name] = Module(name, "v1", default="default")
        for i in range(2, 5):
            self.mods["test1"].add_version("v%d" % i)
            self.mods["test5"].add_version("v%d" % i)

    def load(self, module):
        """Load given module into environment

        Args:
            module: designation of module to load

        Returns:
            Boolean status of module load evaluation"""
        return self.eval("load", module)

    def unload(self, module):
        """Unload given module from environment

        Args:
            module: designation of module to unload

        Returns:
            Boolean status of module unload evaluation"""
        return self.eval("unload", module)

    def save(self):
        """Save loaded modules in default collection

        Returns:
            Boolean status of module save evaluation"""
        return self.eval("save")

    def restore(self):
        """Restore default collection in environment

        Returns:
            Boolean status of module restore evaluation"""
        return self.eval("restore")

    def purge(self):
        """Unload all loaded modules

        Returns:
            Boolean status of module purge evaluation"""
        return self.eval("purge")

    def loaded(self):
        """Return list of loaded modules"""
        if os.environ.get("LOADEDMODULES"):
            loaded = os.environ.get("LOADEDMODULES").split(":")
        else:
            loaded = []
        return loaded

    def __str__(self):
        ret = ""
        for mod in self.mods.values():
            ret += "%s\n" % mod
        return ret

    def __repr__(self):
        self.__str__()


class Module:
    """
    Class to manupulate Module
        name : name of the module
        versions : list of the module versions
        selected : is the module selected for the user
    """

    def __init__(
        self,
        name,
        version,
        selected=False,
        default=False,
    ):

        super().__init__()
        self.name = name
        self.versions = []
        self.default_version = version
        self.current_version = version
        self.selected = selected
        self.whatis = None
        self.help_message = None
        if version is not None:
            self.add_version(version, default)

    def current_designation(self):
        if self.current_version is None:
            designation = self.name
        else:
            designation = os.path.join(self.name, self.current_version)
        return designation

    def default_designation(self):
        if self.default_version is None:
            if not self.versions:
                designation = self.name
            else:
                # get implicit default: highest version number
                latest_version = self.versions.sort(key=LooseVersion)[-1]
                designation = os.path.join(self.name, latest_version)
        else:
            designation = os.path.join(self.name, self.default_version)
        return designation

    def select(self, version=False, isselected=True):
        self.selected = isselected
        if version:
            self.set_version(version)

    def deselect(self):
        self.select(False, False)

    def __str__(self):
        return self.current_designation()

    def __repr__(self):
        self.__str__()

    def desc(self, modulecmd: Modulecmd):
        if self.whatis is None:
            self.whatis = (
                modulecmd.run("whatis", self.default_designation())
                .split(":")[1]
                .strip()
            )
            if not self.whatis:
                self.whatis = self.default_designation()
        return self.whatis

    def help(self, modulecmd: Modulecmd):
        if self.help_message is None:
            self.help_message = modulecmd.run("help", self.default_designation())
            if not self.help_message:
                self.help_message = f"No help for {self.default_designation()}"
        return self.help_message

    def add_version(self, version, default=False):
        self.versions.append(version)
        # print("Module: %s - added version : %s" % (self.name, version))
        if default:
            self.default_version = version

    def set_version(self, version):
        if version in self.versions:
            self.current_version = version
