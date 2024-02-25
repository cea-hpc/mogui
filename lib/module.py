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
        self.savepath = "%s%s%s%s%s" % (
            os.environ["HOME"],
            os.sep,
            ".config/MoGui",
            os.sep,
            "modules",
        )

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

    def save(self, modulelist):
        """
        Save the modulelist to self.savepath
        """
        msg = ""
        for mod in modulelist.values():
            if mod.selected:
                msg += "%s\n" % mod
        try:
            file = open(self.savepath, "w")
            file.write(msg)
        except IOError as e:
            print("Impossible de sauvegarder %s : %s" % (self.savepath, e))

    def load(self, destpath=None):
        """
        Load the modulelist from self.savepath or destpath if specified
        """
        if not destpath:
            destpath = self.savepath
        try:
            file = open(destpath, "r")
            for line in file.readlines():
                line = line.strip()
                if line.startswith("#") or "/" not in line:
                    continue
                (modname, version) = line.rsplit("/", 1)
                if self.mods.get(modname):
                    self.mods[modname].select(version)
                    print(
                        "LOAD: select %s (should be %s)" % (self.mods[modname], version)
                    )
        except IOError as e:
            print("Impossible de lire %s : %s" % (destpath, e))

    def __str__(self):
        ret = ""
        for mod in self.mods.values():
            ret += "%s\n" % mod
        return ret

    def __repr__(self):
        self.__str__()

    def selected(self):
        """Return the list of selected modules"""
        selected = []
        for mod in self.mods.values():
            if mod.selected:
                selected.append(mod)
        return selected


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

    def desc(self):
        if self.whatis is None:
            cmd = Modulecmd()
            self.whatis = (
                cmd.run("whatis", self.default_designation()).split(":")[1].strip()
            )
            if not self.whatis:
                self.whatis = self.default_designation()
        return self.whatis

    def help(self):
        if self.help_message is None:
            cmd = Modulecmd()
            self.help_message = cmd.run("help", self.default_designation())
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
