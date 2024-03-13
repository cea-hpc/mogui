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

from typing import Dict

# Gui PyQt
from PyQt5.QtCore import (
    QEvent,
    QItemSelectionModel,
    QSettings,
    QSize,
    Qt,
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


class MoGui(QMainWindow):
    def __init__(self, modulecmd: Modulecmd, shell_out=None, debug=False):
        super().__init__()
        self.modulecmd = modulecmd
        self.shell_out = shell_out
        self.debug = debug
        self.buttons: Dict[str, QAction] = {}

        QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + ["share/icons"])
        self.set_icon_theme_based_on_palette()

        self.setWindowTitle("MoGui")
        self.setWindowIcon(QIcon.fromTheme("environment-modules"))

        self.create_objects()
        self.readSettings()

    def create_button(self, text: str, icon: str, shortcut: str, call):
        """Initialize a toolbar button"""
        self.buttons[text] = QAction(text, self)
        self.buttons[text].setIcon(QIcon.fromTheme(icon))
        self.buttons[text].setShortcut(shortcut)
        self.buttons[text].triggered.connect(call)
        self.toolbar.addAction(self.buttons[text])

    def create_objects(self):
        """Initialize GUI objects"""
        # Set ToolBar
        self.toolbar = self.addToolBar("&Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.show()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setFloatable(False)

        # Set Actions
        self.create_button("Reset", "edit-undo-symbolic", "Ctrl+Z", self.reset)
        self.create_button("Purge", "edit-clear-symbolic", "Ctrl+P", self.purge)
        self.create_button(
            "Restore", "document-revert-symbolic", "Ctrl+R", self.restore
        )
        self.create_button("Save", "document-save-symbolic", "Ctrl+S", self.save)
        self.create_button("Help", "help-contents-symbolic", "F1", self.help)
        self.create_button("Quit", "application-exit-symbolic", "Ctrl+Q", self.close)

        # Status bar
        self.statusBar()

        # Main frame
        self.mainframe = QFrame(self)
        # Main layout
        self.layout = QHBoxLayout(self.mainframe)
        self.setCentralWidget(self.mainframe)

        # Modules list (with label)
        self.modulelabel = QLabel("Available modules:")
        self.avail_modules = AvailModulesView(self.load, self.unload, self.show_help)

        # Available modules frame
        self.moduleslayout = QVBoxLayout()
        self.moduleslayout.addWidget(self.modulelabel)
        self.moduleslayout.addWidget(self.avail_modules)

        self.layout.addLayout(self.moduleslayout)

        # Loaded modules frame
        self.choiceLabel = QLabel("Currently loaded modules:")
        self.loaded_modules = LoadedModulesView(self.unload, self.show_display)

        self.choicelayout = QVBoxLayout()
        self.choicelayout.addWidget(self.choiceLabel)
        self.choicelayout.addWidget(self.loaded_modules)

        self.layout.addLayout(self.choicelayout)

    def is_palette_dark(self):
        """Return if GUI's color palette is currently in dark mode"""
        return self.palette().window().color().lightnessF() < 0.5

    def set_icon_theme_based_on_palette(self):
        """Set widget icons depending on palette lightness"""
        theme_name = "dark" if self.is_palette_dark() else "light"
        QIcon.setThemeName(theme_name)

    def changeEvent(self, event: QEvent):
        """Trap GUI's color palette change to refresh icons"""
        if event.type() == QEvent.PaletteChange:
            self.set_icon_theme_based_on_palette()

    def setModules(self):
        avail_dict = self.modulecmd.avail(refresh=True)

        # Refresh the available modules widget
        self.avail_modules.refresh(avail_dict)

        loaded_list = []
        for loaded_mod in self.modulecmd.loaded():
            loaded_list.append(avail_dict[loaded_mod])
        # Select loaded modules in the available modules list
        self.avail_modules.select(loaded_list)
        # Refresh the loaded modules widget
        self.loaded_modules.refresh(loaded_list)

    def report_event(self, message, sub=False):
        """Report an event message"""
        if sub:
            prefix = "  * "
        else:
            prefix = ""
        text = prefix + message

        if not sub:
            self.statusBar().showMessage(text)

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

    def show_display(self, position: QPoint, module: Module):
        """Report display info of selected module in WhatsThis window"""
        display_message = module.display(self.modulecmd)
        if len(display_message):
            text = [
                f"<u>Module Display for <b>{module.name}</b></u><br/>",
                display_message.replace("\n", "<br/>"),
            ]
            QWhatsThis.showText(position, "\n".join(text))

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
        self.report_event("Default collection saved")
        self.modulecmd.eval("save")

    def reset(self):
        self.report_event("Initial environment restored")
        self.modulecmd_eval("reset")

    def restore(self):
        self.report_event("Default collection restored")
        self.modulecmd_eval("restore")

    def purge(self):
        self.report_event("Loaded modules purged")
        self.modulecmd_eval("purge")

    def help(self):
        if self.debug:
            print_debug("TODO")

    def writeSettings(self):
        """Save GUI properties in application configuration file"""
        settings = QSettings("environment-modules", "mogui")
        settings.setValue("size", self.size())

    def readSettings(self):
        """Load GUI properties from application configuration file"""
        settings = QSettings("environment-modules", "mogui")
        size = settings.value("size", QSize(400, 400))
        self.resize(size)

    def close(self):
        """Save application properties and quit"""
        self.writeSettings()
        super().close()

    def closeEvent(self, event: QEvent):
        """Properly close application when clicking window manager exit button"""
        self.close()


class ModuleGui(QStandardItem):
    """Represents a module: a name and a version"""

    def __init__(self, module):
        super().__init__(module.name)
        self.setEditable(False)
        self.module = module


class AvailModulesView(QTreeView):
    """List available modules"""

    def __init__(self, load, unload, show_help, parent=None):
        super().__init__(parent)

        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setAnimated(True)
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.MultiSelection)

        self.load = load
        self.unload = unload
        self.clicked.connect(self.on_clicked)

        self.show_help = show_help
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_clicked)

    def refresh(self, avail_module_list: list[Module]):
        """Clear then fill widget with currently available modules"""
        self.model.clear()

        # module keys are already sorted
        mod_name_list = list(avail_module_list.keys())
        for mod_name in mod_name_list:
            item = ModuleGui(avail_module_list[mod_name])
            self.model.appendRow(item)

    def select(self, module_list: list[Module]):
        """Select given modules in the list"""
        selection = self.selectionModel()
        for module in module_list:
            for item in self.model.findItems(module.name):
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


class LoadedModulesView(QListView):
    """List loaded modules"""

    def __init__(self, unload, show_display, parent=None):
        super().__init__(parent)

        self.model = QStandardItemModel()
        self.setModel(self.model)

        self.setUniformItemSizes(True)
        self.setAcceptDrops(True)

        self.unload = unload
        self.doubleClicked.connect(self.on_double_clicked)

        self.show_display = show_display
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_clicked)

    def refresh(self, loaded_module_list: list[Module]):
        """Clear then fill widget with currently loaded modules"""
        self.model.clear()

        for loaded_mod in loaded_module_list:
            mod_item = ModuleGui(loaded_mod)
            mod_item.setSelectable(False)
            self.model.appendRow(mod_item)

    def on_double_clicked(self, index):
        """Unload double clicked item module"""
        module = self.model.item(index.row()).module
        self.unload(module)

    def on_right_clicked(self, position: QPoint):
        """Show display message of selected module item"""
        index = self.indexAt(position)
        module = self.model.item(index.row()).module
        self.show_display(position, module)
