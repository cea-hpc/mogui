#!/usr/bin/python
# -*- coding: utf-8 -*-
# MoGui: Gui frontend for module
# Author: A. Cedeyn
#

#
# TODO:
# - Add Selected property to the Module class

import os, sys, string

from lib.module import Modulecmd
from gui.mogui import MoGui

from PyQt4.QtGui import ( QApplication )

if not os.environ.has_key('MODULEPATH'):
    try:
        paths = open(os.sep.join([ os.environ['MODULESHOME'],
                               "/init/.modulespath"])).readlines()
        paths = [ p.strip() for p in paths if p.startswith(os.sep) ]
        os.environ['MODULEPATH'] = ':'.join(paths)
        print "Module path: %s" % os.environ['MODULEPATH']
    except IOError:
        print "No MODULESPATH found, no module will be loaded"
    except KeyError:
        print "No MODULESHOME found, is module correctly installed ?"
        sys.exit(1)

if not os.environ.has_key('LOADEDMODULES'):
    os.environ['LOADEDMODULES'] = '';

if __name__ == "__main__":
    modules = Modulecmd(modulecmd_path='/opt/Modules/bin/modulecmd.tcl')
    if len(sys.argv) > 1 :
        print string.join(modules.launch(sys.argv[1], sys.argv[2:]))
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

    print modules
    gui = MoGui(modules.mods, modulecmd_path='/opt/Modules/bin/modulecmd.tcl')
    gui.setModules(modules)
    gui.show()

    sys.exit(app.exec_())

