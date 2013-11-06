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
from tempfile import NamedTemporaryFile
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
        self.mods = modules.mods
        # Set the module list to the modulelist widget
        self.modulelist.set(self.mods, add=self.__addToChoice, remove=self.__removeFromChoice)
        # Add selected modules in the choiceList
        for m in modules.selected():
            self.__addToChoice(m)
            # Selected modules in the modulelist
            self.modulelist.select(m)
        # Hack to select all moduleGroup
        self.modulelist.expandAll()
        self.modulelist.collapseAll()
        ##

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
            self.history.append("%s already added !!" % module_str)
        else:
            # Add only the module if it doesn't exist in the choice list
            self.history.append("Try to add %s" % module_str)
            model.appendRow(name)

        self.history.append("%s selected" % module_str)
        self.info.setText(module.help())
        name.setToolTip(module.help())

    def __removeFromChoice(self, module):
        module_str = "%s" % module
        model = self.choiceModel
        chosen = model.findItems(module_str)
        if len(chosen):
            model.removeRow(chosen[0].index().row())
            self.history.append("%s deselected" % module_str)

    def save(self):
        msg = ""
        for mod in self.mods.values():
            if mod.selected:
                msg += "%s\n" % mod
        QMessageBox.information(self, "Sauvegarde des modules",
                                      "Modules to save :\n%s" % msg
                               )
        modules = Modulecmd(modulecmd_path = self.modulecmd)
        modules.save(self.mods)

    def reset(self):
        modules = Modulecmd(modulecmd_path = self.modulecmd)
        modules.modules()
        modules.load()
        ## To remove (only for test)
        modules.test()
        self.choiceModel.clear()
        self.setModules(modules)

    def terminal(self):
        """
            Launch a self.consolecmd with preloaded modules
        """
        modules = Modulecmd(modulecmd_path = self.modulecmd)
        args = []
        for mod in self.mods.values():
            if mod.selected:
                args.append("%s" % mod)
        tmpfile = NamedTemporaryFile(delete=False)
        tmpfile.writelines(modules.launch(command="purge",
                                                    stderr=False, stdout=True))
        tmpfile.write("""
from subprocess import call
import os
for key in os.environ.keys():
    if key not in [ 'TMPDIR', 'LANG', 'HOME', 'USER', 'DISPLAY', 'MODULEPATH' ]:
        del os.environ[key]
os.environ['LOADEDMODULES']=':'
print os.environ
myenv=os.environ
print "%s"
""" % args)
        tmpfile.writelines(modules.launch(command="load", arguments=args,
                                                    stderr=False, stdout=True)[1:])
        tmpfile.write("call([\"%s\"])\n" % self.consolecmd)
        tmpfile.flush()
        print "Launching : %s" % ["python", tmpfile.name, tmpfile]
        commands = Popen(["python", tmpfile.name])
        tmpfile.close()

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

class ModuleGui(QStandardItem):
    """Represents a module: a name and a version"""
    def __init__(self, module, version=None):
        if version :
            super(ModuleGui, self).__init__("%s/%s" % (module.name, version))
        else:
            super(ModuleGui, self).__init__(module.name)
        self.setIcon(QIcon(DEFL_ICON))
        self.setEditable(False)
        self.module = module
        if version:
            self.version = version
        else:
            self.version = module.default_version

class ModuleChoice(QTreeView):
    """List available modules"""
    def __init__(self, parent=None):
        super(ModuleChoice, self).__init__(parent)
 
        self.model=QStandardItemModel()
 
        self.setModel(self.model)
        self.setAnimated(True)
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.add = None
        self.remove = None
        self._expert = False

    def set(self, modules, add=None, remove=None):
        # Create a line in the model with modulename, versions and desc
        self.add = add
        self.remove = remove
        l = list(modules.keys())
        l.sort()
        for m in l:
            header = ModuleGui(modules[m])
            mods = []
            for v in modules[m].versions:
                mod = ModuleGui(modules[m], v)
                mods.append(mod)
            header.appendRows(mods)
            self.model.appendRow(header)
            self.connect(self, SIGNAL("collapsed(QModelIndex)"), self.enableSubtree)
            self.connect(self, SIGNAL("expanded(QModelIndex)"), self.disableSubtree)

    def expert(self):
        self._expert = not self._expert
        if self._expert:
            self.expandAll()
        else:
            self.collapseAll()

    def select(self, module):
        """ Select a module in the list """
        root = self.model.invisibleRootItem()
        selection = self.selectionModel()
        for h in range(0, root.rowCount()):
            header = root.child(h)
            for i in range(0, header.rowCount()):
                child = header.child(i)
                if child.module.name == module.name and \
                       child.version == module.current_version :
                    selection.select(child.index(), QItemSelectionModel.Select)
                    self.select_module(child.index())

    def collapseAll(self):
        root = self.model.invisibleRootItem()
        for i in range(0, root.rowCount()):
            self.collapse(root.child(i).index())

    def selectionChanged(self, selected, deselected):
        """
           Manage selection
           * Only the root item if collapsed
           * Only one child if expanded
        """
        selection = self.selectionModel()
        root = self.model.invisibleRootItem()
        for index in selected.indexes():
            parent = index.parent()
            moduleGroup = self.model.item(parent.row())
            # We selected a version of a module
            if moduleGroup:
                # Only select one element in the subtree
                for i in range(0, moduleGroup.rowCount()):
                    child = moduleGroup.child(i)
                    if child.index() != index:
                        selection.select(child.index(),
                                         QItemSelectionModel.Deselect)
                version = moduleGroup.child(index.row()).version
                moduleGroup.module.select(version)
            else:
                moduleGroup = self.model.item(index.row())
                moduleGroup.module.select()
            module = moduleGroup.module
            print "Selected %s" % module
            self.add(module)
        for index in deselected.indexes():
            parent = index.parent()
            moduleGroup = self.model.item(parent.row())
            # We selected module header
            if not moduleGroup:
                moduleGroup = self.model.item(index.row())
                # We deselect all its childs
                for i in range(0, moduleGroup.rowCount()):
                    child = moduleGroup.child(i)
                    selection.select(child.index(), QItemSelectionModel.Deselect)
            module = moduleGroup.module
            moduleGroup.module.deselect()
            print "Deselected %s" % module
            self.remove(module)
        self.update()

    def enableSubtree(self, index):
        """Enable root item"""
        self.model.item(index.row()).setSelectable(True)
        self.select_module(index)

    def disableSubtree(self, index):
        """Disable root item"""
        self.model.item(index.row()).setSelectable(False)
        self.select_version(index)

    def select_version(self, index):
        # Select subversion item of a module
        item = self.model.item(index.row())
        selection = self.selectionModel()
        selected = selection.isSelected(index)
        for i in range(0, item.rowCount()):
            child = item.child(i)
            if child.text() == "%s" % item.module:
                selected_child = child
        if selected:
            selection.select(selected_child.index(), QItemSelectionModel.Select)

    def select_module(self, index):
        # Select module item of a module version
        item = self.model.item(index.row())
        selection = self.selectionModel()
        # Select root item if at least one subitem is selected
        for i in range(0, item.rowCount()):
            child = item.child(i)
            selected = selection.isSelected(child.index())
            if selected:
                break
        if selected:
            selection.select(index, QItemSelectionModel.Select)
