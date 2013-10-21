#!/usr/bin/python
# -*- coding: utf-8 -*-
# MoGui: Gui frontend for module
# Author: A. Cedeyn
#
# Gui PyQt
from PyQt4.QtCore import (
                        Qt,
                        SIGNAL,
                        SLOT,
                        QSettings,
                        QSize,
                        pyqtSlot,
                        pyqtSignal,
                        )
from PyQt4.QtGui import (
                        QAbstractItemView,
                        QAction,
                        QComboBox,
                        QDialog,
                        QMainWindow,
                        QMessageBox,
                        QHBoxLayout,
                        QIcon,
                        QItemSelectionModel,
                        QItemDelegate,
                        QLabel,
                        QListView,
                        QPushButton,
                        QVBoxLayout,
                        QScrollArea,
                        QTreeView,
                        QFrame,
                        QStandardItemModel,
                        QStandardItem,
                        QTextEdit,
                        QWidget)

# To launch commands
from subprocess import Popen
# Save and restore modules
from lib.module import (Modulecmd, Module)

ICON = "images/accessories-dictionary.png"
RESET_ICON = "images/reload.png"
SAVE_ICON = "images/gtk-save.png"
TERM_ICON = "images/terminal.png"
HELP_ICON = "images/help.png"
QUIT_ICON = "images/gtk-quit.png"
XTERM = "/usr/bin/xterm"

class MoGui(QMainWindow):
    def __init__(self, modules=None,
                       modulecmd_path="/opt/Modules/default/bin/modulecmd"):
        super(MoGui, self).__init__()
        self.mods = modules
        self.setWindowTitle("MoGui")
        self.setWindowIcon(QIcon(ICON))
        self.createObjects()
        self.consolecmd = XTERM
        self.modulecmd = modulecmd_path
        self.readSettings()

    def createObjects(self):

        # Set Actions
        actionReset = QAction("&Reset", self)
        actionReset.setIcon(QIcon(RESET_ICON))
        actionReset.setShortcut("Ctrl-R")
        self.connect(actionReset, SIGNAL("triggered()"), self.reset)

        actionSave = QAction("&Sauver", self)
        actionSave.setIcon(QIcon(SAVE_ICON))
        actionSave.setShortcut("Ctrl-S")
        self.connect(actionSave, SIGNAL("triggered()"), self.save)

        actionTerm = QAction("&Terminal", self)
        actionTerm.setIcon(QIcon(TERM_ICON))
        actionTerm.setShortcut("Ctrl-T")
        self.connect(actionTerm, SIGNAL("triggered()"), self.terminal)

        actionHelp = QAction("&Aide", self)
        actionHelp.setIcon(QIcon(HELP_ICON))
        actionHelp.setShortcut("F1")
        self.connect(actionHelp, SIGNAL("triggered()"), self.help)

        actionQuit = QAction("&Quitter", self)
        actionQuit.setIcon(QIcon(QUIT_ICON))
        actionQuit.setShortcut("Ctrl-Q")
        self.connect(actionQuit, SIGNAL("triggered()"), self.close)

        # Set ToolBar
        self.toolbar = self.addToolBar("&Barre d'outils")
        self.toolbar.setIconSize(QSize(32,32))
        self.toolbar.show()
        self.toolbar.addAction(actionReset)
        self.toolbar.addAction(actionSave)
        self.toolbar.addAction(actionTerm)
        self.toolbar.addAction(actionHelp)
        self.toolbar.addSeparator()
        self.toolbar.addAction(actionQuit)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setFloatable(False)

        # Set Menu
        self.menubar = self.menuBar()
        self.menubar.hide()
        menufile = self.menubar.addMenu("&Fichier")
        menufile.addAction(actionReset)
        menufile.addAction(actionSave)
        menufile.addAction(actionQuit)
        menuaction = self.menubar.addMenu("&Action")
        menuaction.addAction(actionTerm)
        menuhelp = self.menubar.addMenu("&Aide")
        menuhelp.addAction(actionHelp)

        # Main frame
        self.mainframe = QFrame(self)
        # Main layout
        self.layout = QHBoxLayout(self.mainframe)
        self.setCentralWidget(self.mainframe)


        # Modules list (with label)
        self.modulelabel = QLabel("Liste des produits disponibles:")
        self.modulechoice = ModuleChoice()

        # Info about current Module
        self.infolabel = QLabel("Information :")
        self.info = QTextEdit()
        self.info.setReadOnly(True)

        # Actions history
        self.historylabel = QLabel("Historique:")
        self.history = QTextEdit()
        self.history.setReadOnly(True)

        # Module list frame
        self.moduleslayout = QVBoxLayout()
        self.moduleslayout.addWidget(self.modulelabel)
        self.moduleslayout.addWidget(self.modulechoice)
        self.moduleslayout.addWidget(self.infolabel)
        self.moduleslayout.addWidget(self.info)
        self.moduleslayout.addWidget(self.historylabel)
        self.moduleslayout.addWidget(self.history)

        self.layout.addLayout(self.moduleslayout)

        # Module choice frame
        self.choiceLabel = QLabel("Liste des produits choisis:")
        self.choiceModel = QStandardItemModel()
        self.choiceList = QListView()
        self.choiceList.setModel(self.choiceModel)
        self.choiceList.setIconSize(QSize(256,256))
        self.choiceList.setUniformItemSizes(True)
        self.choiceList.setViewMode(QListView.IconMode)
        self.choiceList.setAcceptDrops(True)
        self.choicelayout = QVBoxLayout()

        self.choicelayout.addWidget(self.choiceLabel)
        self.choicelayout.addWidget(self.choiceList)

        self.layout.addLayout(self.choicelayout)

        #Test
        self.connect(self.choiceList, SIGNAL("dropEvent()"), self.dropModule)
        self.connect(actionHelp, SIGNAL("triggered()"), self.modulechoice.expert)

    def setModules(self, modules):
        self.mods = modules
        # Set the module list to the modulechoice widget
        self.modulechoice.set(modules, slot=self.add)

    def dropModule(self, event):
        module_gui = event.mimeData()
        self.addToList(module_gui)

    def add(self):
        """
        Add the specified module/version to the choice list
        We retrieve version and name from the signal sender
        which should be a ModuleGui object where we can fetch
        the module and version name from the both attribute QLabel
         * name
         * version
        """
        module_gui = self.sender()
        self.addToList(module_gui)

    def addToList(self, module_gui):
        modulename = "%s" % module_gui.name.text()
        moduleversion = "%s" % (module_gui.version.text())
        module = "%s/%s" % (modulename, moduleversion)
        chosen = self.choiceModel.findItems(modulename,
                                            flags = Qt.MatchContains) 
        name = QStandardItem(module)
        name.setToolTip(module)
        name.setEditable(False)
        name.setIcon(QIcon("images/module.png"))


        if len(chosen) != 0:
            # Replace the module version if it exists in the choice list
            row = chosen[0].index().row()
            print "Removing module at %d" % row
            self.choiceModel.setItem(row, name)
            # Should be a popup
            print "%s already added !!" % module
        else:
            # Add only the module if it doesn't exist in the choice list
            print "Try to add %s" % module
            self.choiceModel.appendRow(name)

        mod = module_gui.data
        self.history.append("%s selected" % module)
        self.info.setText(mod.help())
        name.setToolTip(mod.help())
        mod.select(True)
        mod.setVersion(moduleversion)


    def save(self):
        msg = ""
        for mod in self.mods.values():
            if mod.selected:
                msg += "%s/%s\n" % (mod.name, mod.current_version)
        QMessageBox.information(self, "Sauvegarde des modules",
                                      "Modules to save :\n%s" % msg
                               )
        cea_module = Modulecmd(modulecmd_path = self.modulecmd)
        cea_module.save(self.mods)

    def reset(self):
        cea_module = Modulecmd(modulecmd_path = self.modulecmd)
        cea_module.modules()
        cea_module.load()
        ## To remove (only for test)
        cea_module.test()
        self.setModules(cea_module.mods)
        self.choiceModel.clear()

    def terminal(self):
        print "TODO"
        commands = Popen([self.consolecmd])

    def help(self):
        print "TODO"

    def writeSettings(self):
        settings = QSettings("MoGui", "gui")
        settings.beginGroup("toolbar")
        settings.setValue("geometry", self.toolbar.geometry())
        settings.endGroup()

    def readSettings(self):
        settings = QSettings("MoGui", "gui")
        settings.beginGroup("toolbar")
        self.toolbar.setGeometry(settings.value("geometry",
                                 self.toolbar.geometry()).toRect())
        settings.endGroup()

    def close(self):
        self.writeSettings()
        super(MoGui, self).close()

class ModuleGui(QWidget):
    """Represents 2 objects of a module: a name and a version"""
    def __init__(self, name, version, data, slot=None, parent=None):
        super(ModuleGui, self).__init__(parent)
        layout = QHBoxLayout(self)
        self.setObjectName("ModuleGui");
        self.setContentsMargins(0,0,0,0)
        self.data = data
        self.name = QLabel(name)
        self.version = QLabel(version)
        self.button = QPushButton("+")
        layout.addWidget(self.name)
        layout.addSpacing(40)
        layout.addWidget(self.version)
        layout.addSpacing(40)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.connect(self.button, SIGNAL("clicked()"),
                     self.selected)

        if slot != None :
            self.connect(self, SIGNAL("selected()"), slot)
            self.connect(self, SIGNAL("clicked()"), slot)


    def selected(self):
        self.emit(SIGNAL("selected()"))

    def mouseReleaseEvent(self, event):  
        self.emit(SIGNAL('clicked()'))

class ModuleChoice(QWidget):
    """List available modules"""
    def __init__(self, parent=None):
        super(ModuleChoice, self).__init__(parent)
 
        self.layout=QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
 
        self.scroll=QScrollArea()
        self.layout.addWidget(self.scroll)
 
        w=QWidget(self)        
        self.vbox=QVBoxLayout(w)
        self.scroll.setWidget(w)

        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #6c6c6c;
                border-radius: 10px;
            }
            QPushButton::hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0,
                                            y2: 1,
                                            stop: 0 #e7effd,
                                            stop: 1 #cbdaf1);
                border-radius: 10px;
            }
            * {
                font-weight: bold;
                background-color: #FFFFFF;
                border-radius: 10px;
            }
            """)

    def set(self, modules, slot=None):
        # Create a line in the model with modulename, versions and desc
        l = list(modules.keys())
        l.sort()
        w=QWidget(self)        
        self.vbox=QVBoxLayout(w)
        for m in l:
            for v in modules[m].versions:
                line = ModuleGui(modules[m].name, v, modules[m], slot=slot)
                self.vbox.addWidget(line)
        self.scroll.setWidget(w)

    def expert(self, expert=True):
        if expert :
            print "Mode expert: hiding unuseful modules"
        else:
            print "Mode expert deactivated: showing all modules"
        for i in range(0, self.vbox.count()):
            line = self.vbox.itemAt(i).widget()
            module = line.data
            print "Module to hide : %s/%s module default: %s" % (
                                              line.name.text(),
                                              line.version.text(),
                                              module.default_version)
            if expert and (line.version.text() != module.default_version) :
                line.hide()
            else:
                line.show()
