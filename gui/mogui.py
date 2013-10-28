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
DEFL_ICON = "images/module.png"
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
        self.defaultIcon = QIcon(DEFL_ICON)
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
        self.modulelist = ModuleChoice()

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
        self.moduleslayout.addWidget(self.modulelist)
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
        #self.choiceList.setViewMode(QListView.IconMode)
        self.choiceList.setAcceptDrops(True)
        self.choicelayout = QVBoxLayout()

        self.choicelayout.addWidget(self.choiceLabel)
        self.choicelayout.addWidget(self.choiceList)

        self.layout.addLayout(self.choicelayout)

        #Test
        self.connect(self.choiceList, SIGNAL("dropEvent()"), self.dropModule)
        self.connect(actionHelp, SIGNAL("triggered()"), self.modulelist.expert)

    def setModules(self, modules):
        self.mods = modules
        # Set the module list to the modulelist widget
        self.modulelist.set(modules, slot=self.add)
        for m in self.mods.keys():
            if self.mods[m].selected:
                self.__addToChoice(self.mods[m])

    def dropModule(self, event):
        module_gui = event.mimeData()
        self._addToList(module_gui)

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
        self._addToChoice(module_gui)

    def _addToChoice(self, module_gui):
        moduleversion = "%s" % (module_gui.version.text())
        module = module_gui.data
        module.select(moduleversion)
        self.__addToChoice(module)

    def __addToChoice(self, module):
        module_str = "%s" % module
        model = self.choiceModel
        try:
            chosen = model.findItems(module.name, flags = Qt.MatchContains)
        except TypeError:
            # If FindItems is not supported create a list from the model
            chosen = []
            for index in range(0, model.rowCount()):
                # The itemData[0] is the text field of the item
                chosen_itemData = model.itemData(model.index(index,0))
                chosen_modulename = chosen_itemData[0].toString()
                if chosen_modulename.startsWith(module.name):
                    chosen.append(model.item(index))

        name = QStandardItem(module_str)
        name.setToolTip(module_str)
        name.setEditable(False)
        name.setIcon(self.defaultIcon)


        if len(chosen) != 0:
            # Replace the module version if it exists in the choice list
            row = chosen[0].index().row()
            model.setItem(row, name)
            # Should be a popup
            print "%s already added !!" % module_str
        else:
            # Add only the module if it doesn't exist in the choice list
            print "Try to add %s" % module_str
            model.appendRow(name)

        self.history.append("%s selected" % module_str)
        self.info.setText(module.help())
        name.setToolTip(module.help())


    def save(self):
        msg = ""
        for mod in self.mods.values():
            if mod.selected:
                msg += "%s\n" % mod
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
        self.choiceModel.clear()
        self.setModules(cea_module.mods)

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
        layout.setContentsMargins(0,0,0,0)
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
        # Deactivate when the module is selected
        # (must enable the other versions)
        #self.button.setEnabled(False)

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
