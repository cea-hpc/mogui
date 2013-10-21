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

    app.setStyleSheet("""
                        QComboBox {
                            background-color: #FFFFFF;
                            show-decoration-selected: 1;
                            border: 1px solid gray ;
                            border-radius: 3px;
                            padding: 1px 18px 1px 3px;
                            max-height: 12px;
                        }

                        QComboBox:selected {
                            background: #418bd4;
                            color: #FFFFFF;
                        }

                        QComboBox:on {
                            /*padding-left: 20px;*/
                        }

                        QComboBox::drop-down {
                            subcontrol-origin: padding;
                            subcontrol-position: bottom right;
                            width: 0px;
                            right: 0px;

                            border-left-width: 1px;
                            border-left-color: darkgray;
                            /* just a single line */
                            border-left-style: solid;
                            /*same radius as the QComboBox*/
                            border-top-right-radius: 3px;
                            border-bottom-right-radius: 3px;
                        }

                        QComboBox QAbstractItemView {
                            background-color: #EEF5F5;
                            border-radius: 3px;
                            opacity: 200;
                        }
                        QTreeView::item {
                            border-radius: 10px;
                        }
                        QTreeView::item {
                            border: 1px solid #d9d9d9;
                            border-top-color: transparent;
                            border-bottom-color: transparent;
                        }

                        QTreeView::item:hover {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0,
                                                        y2: 1,
                                                        stop: 0 #e7effd,
                                                        stop: 1 #cbdaf1);
                            border: 1px solid #bfcde4;
                        }

                        QTreeView::item:selected {
                            border: 1px solid #567dbc;
                        }

                        QTreeView::item:selected:active{
                            background: qlineargradient(x1: 0, y1: 0, x2: 0,
                                                        y2: 1,
                                                        stop: 0 #6ea1f1,
                                                        stop: 1 #567dbc);
                        }

                        QTreeView::item:selected:!active {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0,
                                                        y2: 1,
                                                        stop: 0 #6b9be8,
                                                        stop: 1 #577fbf);
                        }
                        QHeaderView::section {
                            background-color: qlineargradient(x1:0, y1:0, x2:0,
                                                              y2:1,
                                                              stop:0 #616161,
                                                              stop: 0.5 #505050,
                                                              stop: 0.6 #434343,
                                                              stop:1 #656565);
                            color: white;
                            padding-left: 4px;
                            border: 1px solid #6c6c6c;
                            border-radius: 10px;
                        }
                        QTextEdit, QTreeView, QListView, QHeaderView {
                            background-color: #FFFFFF;
                            border-radius: 10px;
                        }
                        QToolButton::hover {
                            background: qlineargradient(x1: 0, y1: 0, x2: 0,
                                                        y2: 1,
                                                        stop: 0 #e7effd,
                                                        stop: 1 #cbdaf1);
                            border-radius: 10px;
                        }
                        QToolBar {
                            background-color: #FFFFFF;
                            border-bottom-left-radius: 10px;
                            border-bottom-right-radius: 10px;
                        }
                        QTreeView, QScrollArea{
                            background-image: url("images/module.png");
                            background-attachment: fixed;
                            background-color: #FFFFFF;
                            border-radius: 10px;
                            background-position: bottom right;
                            background-origin: content;
                            background-repeat: no-repeat;
                        }
                        QScrollBar {
                            width: 5px;
                            border: 0px;
                        }
                        QScrollBar::handle:vertical {
                            border: 0px;
                            background: lightgrey;
                            min-height: 20px;
                            border-radius: 4px;
                        }
                        """);

    print cea_module
    gui = MoGui(cea_module.mods, modulecmd_path='/opt/Modules/bin/modulecmd.tcl')
    gui.setModules(cea_module.mods)
    gui.show()

    sys.exit(app.exec_())

