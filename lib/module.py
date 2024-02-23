#!/usr/bin/python
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

import os, string
from subprocess import Popen, PIPE

DEFAULT_MODULE_PATH='/usr/local/Modules/libexec/modulecmd.tcl'

class Modulecmd(object):
    def __init__(self, shell="python",
                 modulecmd_path=DEFAULT_MODULE_PATH):
        self.shell = shell
        self.mods = {}
        self.modulecmd = modulecmd_path
        self.helppath = '/opt/Modules/%s/description'
        self.savepath = '%s%s%s%s%s' % (os.environ['HOME'], os.sep,
                                  ".config/MoGui", os.sep, "modules")

    def launch(self, command, arguments=[], stderr=True, stdout=False):
        output = []
        try:
            commands = Popen([self.modulecmd, self.shell, command ] + arguments,
                                             stdout=PIPE, stderr=PIPE)
            if stderr:
                output += commands.stderr.readlines()
            if stdout:
                output += (commands.stdout.readlines())
        except OSError as e:
            print("Impossible d'executer la commande %s : %s" % ([self.modulecmd,
                                            self.shell, command ] + arguments, e))

        ## commands starts from the 2nd index to skip the headers
        return output

    def modules(self):
        """
        Fetch all modules available on this environnment
        return a hash table with all modules and their current version
        """
        lines = self.launch("avail", ['-t'])
        version = "1.0"
        desc = None

        for l in lines:
            l = l.decode()
            ## Ignore empty lines and line statring with a path
            if ( l != "\n") and not (l.startswith('/')) and not (l.startswith('--')):
                mod = l.split(None)[0]
                modname = mod.rsplit('/', 1)[0]
                try :
                    version = mod.rsplit('/', 1)[1].split('(')[0]
                except IndexError:
                    version = 'default'
                try :
                    default = mod.rsplit('/', 1)[1].split('(')[1].rstrip(")")
                except IndexError:
                    default = None
                #desc = self.launch("whatis", [mod])[0].strip().split(":")[1].strip()
                if modname in self.mods.keys():
                    self.mods[modname].addVersion(version, default)
                else:
                    self.mods[modname] = Module(modname, version, default=default, description=desc, modulecmd_path=self.modulecmd)
        return self.mods

    def test(self):
        """
        Create fake module list
        """
        for i in range(1,10):
            name = "test%d" % i
            self.mods[name] = Module(name, "v1", default="default",
                                            description="test module %d v1" % i)
        for i in range(2,5):
            self.mods["test1"].addVersion("v%d" % i)
            self.mods["test5"].addVersion("v%d" % i)

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
        except IOError as e :
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
                if line.startswith("#") or '/' not in line:
                    continue
                (modname, version) = line.rsplit('/', 1)
                if self.mods.get(modname) :
                    self.mods[modname].select(version)
                    print("LOAD: select %s (should be %s)" % (self.mods[modname], version))
        except IOError as e :
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

class Module(object):
    """
    Class to manupulate Module
        name : name of the module
        versions : list of the module versions
        selected : is the module selected for the user
        description: the module description
    """
    def __init__(self, name,
                       version,
                       selected=False,
                       default=False,
                       description=None,
                       modulecmd_path=DEFAULT_MODULE_PATH):

        super(Module, self).__init__()
        self.name = name
        self.versions = []
        self.default_version = version
        self.current_version = version
        self.selected = selected
        if description == None :
            description = self.name
        self.description = description
        self.addVersion(version, default)
        self.helpMessage = None
        self.modulecmd = modulecmd_path
        self.desc()

    def select(self, version=False, isselected=True):
        self.selected = isselected
        if version:
            self.setVersion(version)

    def deselect(self):
        self.select(False, False)

    def __str__(self):
        return "%s/%s" % (self.name, self.current_version)

    def __repr__(self):
        self.__str__()

    def desc(self):
        cmd = Modulecmd(modulecmd_path=self.modulecmd)
        try :
            self.description = \
                       cmd.launch("whatis",
                                  ["%s/%s" %
                                   (self.name,
                                   self.default_version),
                                   "0>&2"])[0].decode().strip().split(":")[1].strip()
        except IndexError as e:
            print("Unable to get description of %s : %s" % \
                                                            (self.name, e))
        return self.description

    def help(self):
        cmd = Modulecmd(modulecmd_path=self.modulecmd)
        if not self.helpMessage :
            try :
                helpfile = open(cmd.helppath % self.name)
                self.helpMessage = " ".join([line.decode() for line in helpfile.readlines()])
            except IOError :
                raw_help_message = cmd.launch("help", ["%s/%s" % (self.name, self.default_version)])
                self.helpMessage = " ".join([line.decode() for line in raw_help_message])
        if not self.helpMessage :
            self.helpMessage = "No help for %s" % self.name
        return self.helpMessage

    def addVersion(self, version, default=False):
        self.versions.append(version)
        #print("Module: %s - added version : %s" % (self.name, version))
        if default:
            self.default_version = version

    def setVersion(self, version):
        if version in self.versions:
            self.current_version = version
