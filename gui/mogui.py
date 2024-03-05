# -*- coding: utf-8 -*-

# MOGUI, GUI frontend for module
# Copyright (C) 2011-2024 Aurelien Cedeyn
# Copyright (C)      2024 Xavier Delaruelle
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

# To launch commands
from subprocess import run

# Gui PyQt
from PyQt5.QtCore import (
    QItemSelectionModel,
    QSettings,
    QSize,
    Qt,
    pyqtSignal,
)

from PyQt5.QtGui import (
    QIcon,
    QStandardItem,
    QStandardItemModel,
)

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListView,
    QMainWindow,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
)

from lib.module import Modulecmd, Module
from lib.utils import print_debug

SIGNAL = pyqtSignal

ICON = "images/accessories-dictionary.png"
RESET_ICON = "images/reload.png"
SAVE_ICON = "images/gtk-save.png"
TERM_ICON = "images/terminal.png"
HELP_ICON = "images/help.png"
QUIT_ICON = "images/gtk-quit.png"
DEFL_ICON = "images/module.png"
XTERM = "/usr/bin/xterm"


class MoGui(QMainWindow):
    def __init__(self, modulecmd: Modulecmd, debug=False):
        super().__init__()
        self.modulecmd = modulecmd
        self.debug = debug
        self.setWindowTitle("MoGui")
        self.setWindowIcon(QIcon(ICON))
        self.createObjects()
        self.consolecmd = XTERM
        self.defaultIcon = QIcon(DEFL_ICON)
        self.readSettings()

    def createObjects(self):

        # Set Actions
        actionReset = QAction("&Reset", self)
        actionReset.setIcon(QIcon(RESET_ICON))
        actionReset.setShortcut("Ctrl-R")
        actionReset.triggered.connect(self.reset)

        actionPurge = QAction("&Purge", self)
        actionPurge.setIcon(QIcon(RESET_ICON))
        actionPurge.setShortcut("Ctrl-P")
        actionPurge.triggered.connect(self.purge)

        actionRestore = QAction("&Restore", self)
        actionRestore.setIcon(QIcon(RESET_ICON))
        actionRestore.triggered.connect(self.restore)

        actionSave = QAction("&Sauver", self)
        actionSave.setIcon(QIcon(SAVE_ICON))
        actionSave.setShortcut("Ctrl-S")
        actionSave.triggered.connect(self.save)

        actionTerm = QAction("&Terminal", self)
        actionTerm.setIcon(QIcon(TERM_ICON))
        actionTerm.setShortcut("Ctrl-T")
        actionTerm.triggered.connect(self.terminal)

        actionHelp = QAction("&Aide", self)
        actionHelp.setIcon(QIcon(HELP_ICON))
        actionHelp.setShortcut("F1")
        actionHelp.triggered.connect(self.help)

        actionQuit = QAction("&Quitter", self)
        actionQuit.setIcon(QIcon(QUIT_ICON))
        actionQuit.setShortcut("Ctrl-Q")
        actionQuit.triggered.connect(self.close)

        # Set ToolBar
        self.toolbar = self.addToolBar("&Barre d'outils")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.show()
        self.toolbar.addAction(actionReset)
        self.toolbar.addAction(actionPurge)
        self.toolbar.addAction(actionRestore)
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
        menufile.addAction(actionPurge)
        menufile.addAction(actionRestore)
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
        self.choiceList.setIconSize(QSize(256, 256))
        self.choiceList.setUniformItemSizes(True)
        self.choiceList.setAcceptDrops(True)
        self.choicelayout = QVBoxLayout()

        self.choicelayout.addWidget(self.choiceLabel)
        self.choicelayout.addWidget(self.choiceList)

        self.layout.addLayout(self.choicelayout)

    def setModules(self):
        # Set the module list to the modulelist widget
        self.modulelist.clear()
        self.modulelist.set(
            self.modulecmd.avail(refresh=True), load=self.load, unload=self.unload
        )
        # Add loaded modules in the choiceList
        self.refresh_loaded()
        for m in self.modulecmd.loaded():
            # Selected modules in the modulelist
            self.modulelist.select(m)

    def refresh_loaded(self):
        """Clear choice list and fill it with currently loaded modules"""
        model = self.choiceModel
        model.clear()

        for loaded_mod in self.modulecmd.loaded():
            mod_item = QStandardItem(loaded_mod)
            mod_item.setToolTip(loaded_mod)
            mod_item.setEditable(False)
            mod_item.setIcon(self.defaultIcon)
            model.appendRow(mod_item)

    def report_event(self, message, sub=False):
        """Report an event message"""
        if sub:
            prefix = "  * "
        else:
            prefix = ""
        text = prefix + message

        self.history.append(text)
        if self.debug:
            print_debug(text)

    def modulecmd_eval(self, *arguments):
        """Evaluate module command, refresh widgets and report module changes

        Args:
            arguments: list of module command and its arguments
        """
        loaded_before = self.modulecmd.loaded()
        self.modulecmd.eval(*arguments)
        loaded_after = self.modulecmd.loaded()

        # refresh widgets
        self.setModules()

        # report module changes
        loaded_before.reverse()
        for module in loaded_before:
            if module not in loaded_after:
                self.report_event(f"'{module}' unloaded", True)
        for module in loaded_after:
            if module not in loaded_before:
                self.report_event(f"'{module}' loaded", True)

    def load(self, module: Module):
        """Load specified module"""
        self.report_event(f"Module '{module}' selected")
        self.modulecmd_eval("load", str(module))
        self.info.setText(module.help(self.modulecmd))

    def unload(self, module: Module):
        """Unload specified module"""
        self.report_event(f"Module '{module}' deselected")
        self.modulecmd_eval("unload", str(module))

    def save(self):
        self.report_event("Save loaded environment as default collection")
        self.modulecmd.eval("save")

    def reset(self):
        self.report_event("Reset to initial environment")
        self.modulecmd_eval("reset")

    def restore(self):
        self.report_event("Restore default collection's environment")
        self.modulecmd_eval("restore")

    def purge(self):
        self.report_event("Purge loaded modules")
        self.modulecmd_eval("purge")

    def terminal(self):
        """Launch self.consolecmd terminal that inherits GUI's environment"""
        run(self.consolecmd, check=False)

    def help(self):
        if self.debug:
            print_debug("TODO")

    def writeSettings(self):
        settings = QSettings("MoGui", "gui")
        settings.beginGroup("toolbar")
        settings.setValue("geometry", self.toolbar.geometry())
        settings.endGroup()

    def readSettings(self):
        settings = QSettings("MoGui", "gui")
        settings.beginGroup("toolbar")
        self.toolbar.setGeometry(settings.value("geometry", self.toolbar.geometry()))
        settings.endGroup()

    def close(self):
        self.writeSettings()
        super().close()


class ModuleGui(QStandardItem):
    """Represents a module: a name and a version"""

    def __init__(self, module):
        super().__init__(module.name)
        self.setIcon(QIcon(DEFL_ICON))
        self.setEditable(False)
        self.module = module


class ModuleChoice(QTreeView):
    """List available modules"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setAnimated(True)
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.MultiSelection)

        self.load = None
        self.unload = None
        self.clicked.connect(self.on_clicked)

    def set(self, modules, load=None, unload=None):
        # Create a line in the model with module name
        self.load = load
        self.unload = unload
        mod_name_list = list(modules.keys())
        mod_name_list.sort()
        for mod_name in mod_name_list:
            item = ModuleGui(modules[mod_name])
            self.model.appendRow(item)

    def select(self, module: str):
        """Select a module in the list"""
        selection = self.selectionModel()
        for item in self.model.findItems(module):
            selection.select(item.index(), QItemSelectionModel.Select)

    def on_clicked(self, index):
        """Load or unload selected or deselected item module"""
        module = self.model.item(index.row()).module
        if self.selectionModel().isSelected(index):
            self.load(module)
        else:
            self.unload(module)

    def clear(self):
        """Clear all items"""
        self.model.clear()
