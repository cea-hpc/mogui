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
                        )
from PyQt4.QtGui import (
                        QAbstractItemView,
                        QAction,
                        QComboBox,
                        QMainWindow,
                        QMessageBox,
                        QIcon,
                        QItemSelectionModel,
                        QItemDelegate,
                        QLabel,
                        QVBoxLayout,
                        QTreeView,
                        QFrame,
                        QStandardItemModel,
                        QStandardItem,
                        QTextEdit)

# To launch commands
from subprocess import Popen
# Save and restore modules
from lib.module import Modulecmd

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
        #self.toolbar.setIconSize(QSize(16,16))
        self.toolbar.setIconSize(QSize(32,32))
        self.toolbar.show()
        self.toolbar.addAction(actionReset)
        self.toolbar.addAction(actionSave)
        self.toolbar.addAction(actionTerm)
        self.toolbar.addAction(actionHelp)
        self.toolbar.addSeparator()
        self.toolbar.addAction(actionQuit)
        #self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setFloatable(False)

        # Set Menu
        self.menubar = self.menuBar()
        #self.menubar.show()
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

        # Modules list (with label)
        self.modulelabel = QLabel("Liste des produits disponibles:")
        self.modulesModel = QStandardItemModel()
        self.list = QTreeView()
        self.modulesCombo = VersionCombo(self.list)
        self.list.setItemDelegateForColumn(1, self.modulesCombo)
        self.list.setModel(self.modulesModel)
        self.list.setSortingEnabled(True)
        self.list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list.setMinimumSize(QSize(800,600))
        self.list.setUniformRowHeights(True)

        # Info about current Module
        self.infolabel = QLabel("Information :")
        self.info = QTextEdit()
        self.info.setReadOnly(True)

        # Actions history
        self.historylabel = QLabel("Historique:")
        self.history = QTextEdit()
        self.history.setReadOnly(True)

        self.layout = QVBoxLayout(self.mainframe)
        self.layout.addWidget(self.modulelabel)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.infolabel)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.historylabel)
        self.layout.addWidget(self.history)
        self.setCentralWidget(self.mainframe)

        self.connect(self.list.selectionModel(),
                     SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                     self.selectModule)


    def selectModule(self, selected, deselected):
        #mod = self.list.selectedIndexes()[0].data(Qt.UserRole).toPyObject()
        #mod = self.list.currentIndex().data(Qt.UserRole).toPyObject()
        for i in selected.indexes():
            mod = i.data(Qt.UserRole).toPyObject()
            if not mod.selected :
                self.mods[mod.name].select(True)
                action = "Selection"
                self.info.setText(mod.help())
                self.history.append("%s du module %s (version %s)" %
                                     (action, mod.name, mod.default_version) )
                #i.setCheckState(Qt.Checked)

        for i in deselected.indexes():
            mod = i.data(Qt.UserRole).toPyObject()
            if mod.selected :
                self.mods[mod.name].select(False)
                action = "Deselection"
                self.history.append("%s du module %s (version %s)" %
                                     (action, mod.name, mod.default_version) )

    def setModules(self, elmt):
        self.mods = elmt
        self.modulesModel.clear()
        # Get module lista and sort it
        l = list(elmt.keys())
        l.sort()
        # Create a line in the model with modulename, versions and desc
        for e in l:
            name = QStandardItem(elmt[e].name)
            name.setToolTip(elmt[e].name)
            name.setData(elmt[e], Qt.UserRole)
            name.setEditable(False)

            version = QStandardItem()
            version.setData(elmt[e], Qt.UserRole)
            version.setEditable(True)

            desc = QStandardItem(elmt[e].description)
            desc.setData(elmt[e], Qt.UserRole)
            desc.setEditable(False)

            line = [ name, version, desc ]
            self.modulesModel.appendRow(line)

            if elmt[e].selected :
                selection = self.list.selectionModel().selection()
                selection.select(self.modulesModel.indexFromItem(name),
                                 self.modulesModel.indexFromItem(desc))
                self.list.selectionModel().select(
                    selection,
                    QItemSelectionModel.SelectCurrent)
        self.modulesModel.setHorizontalHeaderLabels(["Modules",
                                                     "Version",
                                                     "Description"])
        self.list.resizeColumnToContents(0)
        self.list.resizeColumnToContents(1)
        self.list.resizeColumnToContents(2)
        for row in range(0, self.modulesModel.rowCount()):
            self.list.openPersistentEditor(self.modulesModel.index(row,1))


    def save(self):
        msg = ""
        for mod in self.mods.values():
            if mod.selected:
                msg += "%s/%s\n" % (mod.name, mod.default_version)
        QMessageBox.information(self, u"Sauvegarde des modules",
                                      "Liste des modules à sauver :\n%s" % msg
                               )
        cea_module = Modulecmd(modulecmd_path = self.modulecmd)
        cea_module.save(self.mods)

    def reset(self):
        cea_module = Modulecmd(modulecmd_path = self.modulecmd)
        cea_module.modules()
        cea_module.load()
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

class VersionCombo(QItemDelegate):
    """Class to correctly edit the version fields"""
    def __init__(self, parent):
        super(QItemDelegate,self).__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        module = index.data(Qt.UserRole).toPyObject()
        for v in module.versions:
            combo.addItem(v, module)
        combo.setStyleSheet("""
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
                            """);

        self.connect(combo, SIGNAL("currentIndexChanged(int)"),
                     self, SLOT("currentIndexChanged()"))
        return combo

    def setModelData(self, editor, model, index):
        model.setData(index, editor.itemData(editor.currentIndex()))

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
