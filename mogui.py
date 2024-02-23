#!/usr/bin/python
# -*- coding: utf-8 -*-

# MOGUI, GUI frontend for module
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

# TODO:
# - Add Selected property to the Module class

import os, sys, string

from lib.module import Modulecmd, DEFAULT_MODULE_PATH
from gui.mogui import MoGui

from PyQt5.QtWidgets import ( QApplication )


if not os.environ.get('MODULEPATH'):
    try:
        paths = open(os.sep.join([ os.environ['MODULESHOME'],
                               "/init/.modulespath"])).readlines()
        paths = [ p.strip() for p in paths if p.startswith(os.sep) ]
        os.environ['MODULEPATH'] = ':'.join(paths)
        print("Module path: %s" % os.environ['MODULEPATH'])
    except IOError:
        print("No MODULESPATH found, no module will be loaded")
    except KeyError:
        print("No MODULESHOME found, is module correctly installed ?")
        sys.exit(1)

if not os.environ.get('LOADEDMODULES'):
    os.environ['LOADEDMODULES'] = '';

if __name__ == "__main__":
    modules = Modulecmd(modulecmd_path=DEFAULT_MODULE_PATH)
    if len(sys.argv) > 1 :
        print("".join(modules.launch(sys.argv[1], sys.argv[2:])))
        sys.exit(0)
    modules.modules()
    modules.load()
    modules.test()

    # Init in Qt gui mode
    app = QApplication(sys.argv)
    app.setOrganizationName("cea")
    app.setApplicationName("MoGui")
    app.setOrganizationDomain("cea.fr")

    try:
        qss = os.sep.join([os.environ["HOME"], ".config/MoGui", "mogui.qss"])
        app.setStyleSheet("".join(open(qss).readlines()))
    except IOError:
        pass

    print(modules)
    gui = MoGui(modules.mods, modulecmd_path=DEFAULT_MODULE_PATH)
    gui.setModules(modules)
    gui.show()

    sys.exit(app.exec_())

