#!/usr/bin/python
# -*- coding: utf-8 -*-
# MoGui: Gui frontend for module
# Author: A. Cedeyn
#

import os, string
from subprocess import Popen, PIPE

class Modulecmd(object):
    def __init__(self, shell="python",
                       modulecmd_path='/opt/Modules/default/bin/modulecmd'):
        self.shell = shell
        self.mods = {}
        self.modulecmd = modulecmd_path
        self.helppath = '/opt/Modules/%s/description'
        self.savepath = '%s%s%s%s%s' % (os.environ['HOME'], os.sep,
                                  ".config/MoGui", os.sep, "modules")

    def launch(self, command, arguments=[]):
        output = []
        try:
            commands = Popen([self.modulecmd, self.shell, command ] + arguments,
                                             stdout=PIPE, stderr=PIPE)
            output = commands.stderr.readlines()
        except OSError, e:
            print "Impossible d'executer la commande %s : %s" % ([self.modulecmd,
                                            self.shell, command ] + arguments, e)

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
        except IOError, e :
            print "Impossible de sauvegarder %s : %s" % (self.savepath, e)

    def load(self, destpath=None):
        """
        Save the modulelist from self.savepath or destpath if specified
        """
        if not destpath:
            destpath = self.savepath
        try:
            file = open(destpath, "r")
            for line in file.readlines():
                (modname, version) = line.rsplit('/', 1)
                if self.mods[modname] :
                    self.mods[modname].select()
                    self.mods[modname].current_version = version
        except IOError, e :
            print "Impossible de lire %s : %s" % (destpath, e)

    def __str__(self):
        ret = ""
        for mod in self.mods.values():
            ret += "%s\n" % mod
        return ret

    def __repr__(self):
        self.__str__()

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
                       modulecmd_path='/opt/Modules/default/bin/modulecmd'):

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

    def select(self, isselected=True):
        self.selected = isselected

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
                                   "0>&2"])[0].strip().split(":")[1].strip()
        except IndexError, e:
            print "Unable to get description of %s : %s" % \
                                                            (self.name, e)
        return self.description

    def help(self):
        cmd = Modulecmd(modulecmd_path=self.modulecmd)
        if not self.helpMessage :
            try :
                self.helpMessage = string.join(open(cmd.helppath % self.name).readlines())
            except IOError :
                self.helpMessage = string.join(cmd.launch("help", ["%s/%s" % (self.name, self.default_version)]))
        if not self.helpMessage :
            self.helpMessage = "No help for %s" % self.name
        return self.helpMessage

    def addVersion(self, version, default=False):
        self.versions.append(version)
        #print "Module: %s - added version : %s" % (self.name, version)
        if default:
            self.default_version = version

    def setVersion(self, version):
        if version in self.versions:
            self.current_version = version
