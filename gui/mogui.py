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

import math
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
    QHeaderView,
    QLabel,
    QMainWindow,
    QTableView,
    QTabWidget,
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
        self.main_frame = QFrame(self)
        self.setCentralWidget(self.main_frame)

        # Available modules list
        self.avail_modules = AvailModulesView(self.load, self.unload, self.show_help)

        # Loaded modules frame
        self.loaded_label = QLabel("Currently loaded modules")
        self.loaded_modules = LoadedModulesView(self.unload, self.show_display)

        # Tab
        self.tab = QTabWidget(self)
        self.tab.addTab(self.avail_modules, "Available modules")

        # Main layout
        self.layout = QVBoxLayout(self.main_frame)
        self.layout.addWidget(self.tab)
        self.layout.addWidget(self.loaded_label)
        self.layout.addWidget(self.loaded_modules)

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
        self.avail_modules.refresh(list(avail_dict.values()))

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
        """Show application help in WhatsThis window"""
        text = [
            "<h2>Help for MoGui application</h2>",
            "<p>MoGui shows currently loaded module environment and enables to update\
                current shell session.</p>",
            "<h3>Toolbar</h3>",
            "<ul>",
            "<li><b>Reset</b>: restore initial environment</li>",
            "<li><b>Purge</b>: unload all loaded modules</li>",
            "<li><b>Restore</b>: load environment described in <i>default</i> collection</li>",
            "<li><b>Save</b>: record currently loaded environment in <i>default</i>\
                collection</li>",
            "<li><b>Help</b>: show this informational page</li>",
            "<li><b>Quit</b>: terminate this application</li>",
            "</ul>",
            "<h3>Available modules</h3>",
            "<p>This section of the application lists the environment modules available\
                in the currently enabled modulepaths.</p>",
            "<ul>",
            "<li><b>Click on an unselected module item</b>: load corresponding module</li>",
            "<li><b>Click on a selected module item</b>: unload corresponding loaded\
                module</li>",
            "<li><b>Right click</b>: display help of selected module item</li>",
            "</ul>",
            "<h3>Loaded modules</h3>",
            "<p>This section of the application lists the environment modules currently\
            loaded.</p>",
            "<ul>",
            "<li><b>Double click</b>: unload selected module</li>"
            "<li><b>Right click</b>: display content of selected module</li>",
            "</ul>",
        ]
        QWhatsThis.showText(self.pos(), "\n".join(text))

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


class AvailModulesView(QTableView):
    """List available modules"""

    def __init__(self, load, unload, show_help, parent=None):
        super().__init__(parent)

        # initial properties (table is empty)
        self.module_list = []
        self.rows_per_col = 1
        self.fixed_cols = 8

        self.model = QStandardItemModel()
        self.setModel(self.model)

        # hide headers
        horizontal_header = QHeaderView(Qt.Horizontal)
        vertical_header = QHeaderView(Qt.Vertical)
        horizontal_header.setVisible(False)
        vertical_header.setVisible(False)
        self.setHorizontalHeader(horizontal_header)
        self.setVerticalHeader(vertical_header)

        # multiple items can be individually selected in table
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
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
        self.module_list = avail_module_list

        # fill table with available modules
        self.rows_per_col = math.ceil(len(self.module_list) / self.fixed_cols)
        col = 0
        row = 0
        for module in self.module_list:
            item = ModuleGui(module)
            self.model.setItem(row, col, item)
            row += 1
            if row == self.rows_per_col:
                col += 1
                row = 0

    def get_module_row_and_col(self, module: str):
        """Return list of row and column indexes in table for specified module"""
        module_list_index = self.module_list.index(module)
        col = math.floor(module_list_index / self.rows_per_col)
        row = module_list_index % self.rows_per_col
        return [row, col]

    def select(self, module_list: list[Module]):
        """Select given modules in the list"""
        selection = self.selectionModel()
        for module in module_list:
            row, col = self.get_module_row_and_col(module)
            item_index = self.model.item(row, col).index()
            selection.select(item_index, QItemSelectionModel.Select)

    def on_clicked(self, index):
        """Load or unload selected or deselected item module"""
        module = self.model.item(index.row(), index.column()).module
        if self.selectionModel().isSelected(index):
            self.load(module)
        else:
            self.unload(module)

    def on_right_clicked(self, position: QPoint):
        """Show help message of selected module item"""
        index = self.indexAt(position)
        module = self.model.item(index.row(), index.column()).module
        absolute_position = self.pos() + position
        self.show_help(absolute_position, module)


class LoadedModulesView(QTableView):
    """List loaded modules"""

    def __init__(self, unload, show_display, parent=None):
        super().__init__(parent)

        # initial properties (table is empty)
        self.mod_name_list = []
        self.rows_per_col = 1
        self.fixed_cols = 8

        self.model = QStandardItemModel()
        self.setModel(self.model)

        # hide headers
        horizontal_header = QHeaderView(Qt.Horizontal)
        vertical_header = QHeaderView(Qt.Vertical)
        horizontal_header.setVisible(False)
        vertical_header.setVisible(False)
        self.setHorizontalHeader(horizontal_header)
        self.setVerticalHeader(vertical_header)

        self.unload = unload
        self.doubleClicked.connect(self.on_double_clicked)

        self.show_display = show_display
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_right_clicked)

    def refresh(self, loaded_module_list: list[Module]):
        """Clear then fill widget with currently loaded modules"""
        self.model.clear()

        # fill table with loaded modules
        self.rows_per_col = math.ceil(len(loaded_module_list) / self.fixed_cols)
        col = 0
        row = 0
        for loaded_mod in loaded_module_list:
            mod_item = ModuleGui(loaded_mod)
            mod_item.setSelectable(False)
            self.model.setItem(row, col, mod_item)
            row += 1
            if row == self.rows_per_col:
                col += 1
                row = 0

    def on_double_clicked(self, index):
        """Unload double clicked item module"""
        module = self.model.item(index.row(), index.column()).module
        self.unload(module)

    def on_right_clicked(self, position: QPoint):
        """Show display message of selected module item"""
        index = self.indexAt(position)
        module = self.model.item(index.row(), index.column()).module
        absolute_position = self.pos() + position
        self.show_display(absolute_position, module)
