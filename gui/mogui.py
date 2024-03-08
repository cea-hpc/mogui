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
    QPoint,
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
    QTreeView,
    QVBoxLayout,
    QWhatsThis,
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
    def __init__(self, modulecmd: Modulecmd, shell_out=None, debug=False):
        super().__init__()
        self.modulecmd = modulecmd
        self.shell_out = shell_out
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
        self.avail_modules = AvailModulesView()

        # Available modules frame
        self.moduleslayout = QVBoxLayout()
        self.moduleslayout.addWidget(self.modulelabel)
        self.moduleslayout.addWidget(self.avail_modules)

        self.layout.addLayout(self.moduleslayout)

        # Loaded modules frame
        self.choiceLabel = QLabel("Liste des produits choisis:")
        self.loaded_modules = LoadedModulesView()

        self.choicelayout = QVBoxLayout()
        self.choicelayout.addWidget(self.choiceLabel)
        self.choicelayout.addWidget(self.loaded_modules)

        self.layout.addLayout(self.choicelayout)

    def setModules(self):
        # Refresh the available modules widget
        self.avail_modules.clear()
        self.avail_modules.set(
            self.modulecmd.avail(refresh=True),
            load=self.load,
            unload=self.unload,
            show_help=self.show_help,
        )
        # Select loaded modules in the available modules list
        for loaded_mod in self.modulecmd.loaded():
            # Selected modules in the avail_modules
            self.avail_modules.select(loaded_mod)
        # Refresh the loaded modules widget
        self.loaded_modules.refresh(self.modulecmd.loaded())

    def report_event(self, message, sub=False):
        """Report an event message"""
        if sub:
            prefix = "  * "
        else:
            prefix = ""
        text = prefix + message

        if self.debug:
            print_debug(text)

    def modulecmd_print_out(self, *arguments):
        """Print on stdout environment change code produced by module command for
        configured out shell

        Args:
            arguments: list of module command and its arguments
        """
        if self.shell_out:
            content = self.modulecmd.run(
                *arguments,
                out_shell=self.shell_out,
                return_content="out",
                silent_err=True,
            )
            if content:
                print(content)

    def modulecmd_eval(self, *arguments):
        """Evaluate module command, refresh widgets and report module changes

        Args:
            arguments: list of module command and its arguments
        """
        loaded_before = self.modulecmd.loaded()
        self.modulecmd_print_out(*arguments)
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

    def unload(self, module: Module):
        """Unload specified module"""
        self.report_event(f"Module '{module}' deselected")
        self.modulecmd_eval("unload", str(module))

    def show_help(self, position: QPoint, module: Module):
        """Report help info of selected module in WhatsThis window"""
        help_message = module.help(self.modulecmd)
        if len(help_message):
            text = [
                f"<u>Module Help for <b>{module.name}</b></u><br/>",
                help_message.replace("\n", "<br/>"),
            ]
            QWhatsThis.showText(position, "\n".join(text))

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


class AvailModulesView(QTreeView):
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

        self.show_help = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_clicked)

    def set(self, modules, load=None, unload=None, show_help=None):
        # Create a line in the model with module name
        self.load = load
        self.unload = unload
        self.show_help = show_help
        # module keys are already sorted
        mod_name_list = list(modules.keys())
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

    def on_right_clicked(self, position: QPoint):
        """Show help message of selected module item"""
        index = self.indexAt(position)
        module = self.model.item(index.row()).module
        self.show_help(position, module)

    def clear(self):
        """Clear all items"""
        self.model.clear()


class LoadedModulesView(QListView):
    """List loaded modules"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = QStandardItemModel()
        self.setModel(self.model)

        self.setUniformItemSizes(True)
        self.setAcceptDrops(True)

    def refresh(self, loaded_module_list: list):
        """Clear then fill widget with currently loaded modules"""
        self.model.clear()

        for loaded_mod in loaded_module_list:
            mod_item = QStandardItem(loaded_mod)
            mod_item.setToolTip(loaded_mod)
            mod_item.setEditable(False)
            self.model.appendRow(mod_item)
