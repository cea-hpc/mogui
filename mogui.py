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
    os.environ['MODULEPATH'] = os.popen("""sed -n 's/[  #].*$//; /./H; $ { x; s/^\\n//; s/\\n/:/g; p; }' ${MODULESHOME}/init/.modulespath""").readline()
    print "Module path: %s" % os.environ['MODULEPATH']

if not os.environ.has_key('LOADEDMODULES'):
    os.environ['LOADEDMODULES'] = '';

if __name__ == "__main__":
    cea_module = Modulecmd(modulecmd_path='/opt/Modules/bin/modulecmd.tcl')
    if len(sys.argv) > 1 :
        print string.join(cea_module.launch(sys.argv[1], sys.argv[2:]))
        sys.exit(0)
    cea_module.modules()
    cea_module.load()
    cea_module.test()

    # Init in Qt gui mode
    app = QApplication(sys.argv)
    app.setOrganizationName("cea")
    app.setApplicationName("MoGui")
    app.setOrganizationDomain("cea.fr")

    print cea_module
    gui = MoGui(cea_module.mods, modulecmd_path='/opt/Modules/bin/modulecmd.tcl')
    gui.setModules(cea_module.mods)
    gui.show()

    sys.exit(app.exec_())

