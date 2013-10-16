#!/usr/bin/python
# -*- coding: utf-8 -*-
# MoGui: Gui frontend for module
# Author: A. Cedeyn
#

#
# TODO:
# - Add Selected property to the Module class

import os, sys, string
from subprocess import Popen, STDOUT, PIPE

# Gui PyQt
from PyQt4.QtCore import (
                        Qt,
                        SIGNAL,
                        SLOT,
                        QVariant,
                        QSettings,
                        QSize,
                        pyqtSlot,
                        QString,
                        QObject)
from PyQt4.QtGui import (
                        QAbstractItemView,
                        QAction,
                        QApplication,
                        QCheckBox,
                        QComboBox,
                        QMainWindow,
                        QMessageBox,
                        QIcon,
                        QItemSelectionModel,
                        QItemDelegate,
                        QLabel,
                        QVBoxLayout,
                        QHeaderView,
                        QListView,
                        QTreeView,
                        QTableView,
                        QTreeWidget,
                        QPushButton,
                        QFrame,
                        QSpacerItem,
                        QStandardItemModel,
                        QStandardItem,
                        QTextEdit)

if not os.environ.has_key('MODULEPATH'):
    os.environ['MODULEPATH'] = os.popen("""sed -n 's/[  #].*$//; /./H; $ { x; s/^\\n//; s/\\n/:/g; p; }' ${MODULESHOME}/init/.modulespath""").readline()
    print "Module path: %s" % os.environ['MODULEPATH']

if not os.environ.has_key('LOADEDMODULES'):
    os.environ['LOADEDMODULES'] = '';

class Modulecmd(object):
    def __init__(self, shell="python",
                       modulecmd_path='/opt/Modules/default/bin/modulecmd'):
        self.shell = shell
        self.mods = {}
        self.modulecmd = modulecmd_path
        self.helppath = '/opt/Modules/%s/description'
        self.savepath = '%s%s%s%s%s' % (os.environ['HOME'], os.sep,
                                  ".mogui", os.sep, "modules")

    def launch(self, command, arguments=[]):
        output = []
        try:
            commands = Popen([self.modulecmd, self.shell, command ] + arguments,
                                             stdout=PIPE, stderr=PIPE)
            output = commands.stderr.readlines()
        except OSError, e:
            print "Impossible d'executer la commande %s : %s" % ([self.modulecmd,
                                            self.shell, command ] + arguments, e)
        #output += commands.stdout.readlines()

        # If we wanted to exec the module result:
        #exec output

        ####catch possible changes to PYTHONPATH environment variable
        #if os.environ.has_key('PYTHONPATH'):
        #    pp = ['']
        #    pythonpath = os.environ['PYTHONPATH'].split(":")
        #    pp.extend(pythonpath)
        #    for p in sys.path:
        #      if (p not in pp) and (p):
        #        pp.append(p)
        #     sys.path = pp

        ## commands starts from the 2nd index to skip the headers
        return output

    def modules(self):
        """
        Fetch all modules available on this environnment
        return a hash table with all modules and their current version
        """
        lines = self.launch("avail", ['-t'])
        version = "1.0"
        desc = None

        for l in lines:
            ## Ignore empty lines and line statring with a path
            if ( l != "\n") and not (l.startswith('/')) and not (l.startswith('--')):
                mod = l.split(None)[0]
                modname = mod.rsplit('/', 1)[0]
                try :
                    version = mod.rsplit('/', 1)[1].split('(')[0]
                except IndexError:
                    version = 'default'
                try :
                    default = mod.rsplit('/', 1)[1].split('(')[1].rstrip(")")
                except IndexError:
                    default = None
                #desc = self.launch("whatis", [mod])[0].strip().split(":")[1].strip()
                if modname in self.mods.keys():
                    self.mods[modname].addVersion(version, default)
                else:
                    self.mods[modname] = Module(modname, version, default=default, description=desc, modulecmd_path=self.modulecmd)
        return self.mods

    def test(self):
        """
        Create fake module list
        """
        self.mods["test1"] = Module("test1", "v1", default="default",
                                        description="test module 1")
        self.mods["test1"].addVersion("v2")
        self.mods["test2"] = Module("test2", "v1", default="default",
                                        description="test module 2")

    def save(self, modulelist):
        """
        Save the modulelist to self.savepath
        """
        msg = ""
        for mod in modulelist.values():
            if mod.selected:
                msg += "%s/%s\n" % (mod.name, mod.default_version)
        try:
            file = open(self.savepath, "w")
            file.write(msg)
        except IOError, e :
            print "Impossible de sauvegarder %s : %s" % (self.savepath, e)

    def load(self, destpath=None):
        """
        Save the modulelist from self.savepath or destpath if specified
        """
        if not destpath:
            destpath = self.savepath
        try:
            file = open(destpath, "r")
            for line in file.readlines():
                (modname, version) = line.rsplit('/', 1)
                if self.mods[modname] :
                    self.mods[modname].select()
                    self.mods[modname].current_version = version
        except IOError, e :
            print "Impossible de lire %s : %s" % (destpath, e)

    def __str__(self):
        ret = ""
        for mod in self.mods.values():
            ret += "%s\n" % mod
        return ret

    def __repr__(self):
        self.__str__()

class Module(object):
    """
    Class to manupulate Module
        name : name of the module
        versions : list of the module versions
        selected : is the module selected for the user
        description: the module description
    """
    def __init__(self, name,
                       version,
                       selected=False,
                       default=False,
                       description=None,
                       modulecmd_path='/opt/Modules/default/bin/modulecmd'):

        super(Module, self).__init__()
        self.name = name
        self.versions = []
        self.default_version = version
        self.current_version = version
        self.selected = selected
        if description == None :
            description = self.name
        self.description = description
        self.addVersion(version, default)
        self.helpMessage = None
        self.modulecmd = modulecmd_path
        self.desc()

    def select(self, isselected=True):
        self.selected = isselected

    def __str__(self):
        return "%s/%s %s" % (self.name, string.join(self.versions, "/"), self.selected)

    def __repr__(self):
        self.__str__()

    def desc(self):
        cmd = Modulecmd(modulecmd_path=self.modulecmd)
        try :
            self.description = \
                       cmd.launch("whatis",
                                  ["%s/%s" %
                                   (self.name,
                                   self.default_version),
                                   "0>&2"])[0].strip().split(":")[1].strip()
        except IndexError, e:
            print "Unable to get description of %s : %s" % \
                                                            (self.name, e)
        return self.description

    def help(self):
        cmd = Modulecmd(modulecmd_path=self.modulecmd)
        if not self.helpMessage :
            try :
                self.helpMessage = string.join(open(cmd.helppath % self.name).readlines())
            except IOError :
                self.helpMessage = string.join(cmd.launch("help", ["%s/%s" % (self.name, self.default_version)]))
        if not self.helpMessage :
            self.helpMessage = "No help for %s" % self.name
        return self.helpMessage

    def addVersion(self, version, default=False):
        self.versions.append(version)
        #print "Module: %s - added version : %s" % (self.name, version)
        if default:
            self.default_version = version

class MoGui(QMainWindow):
    def __init__(self, modules=None):
        super(MoGui, self).__init__()
        self.mods = modules
        self.setWindowTitle("MoGui")
        self.setWindowIcon(QIcon(
            "/usr/share/icons/gnome/32x32/apps/accessories-dictionary.png"))
        self.createObjects()
        self.consolecmd = '/usr/bin/xterm'
        self.readSettings()

    def createObjects(self):

        # Set Actions
        actionReset = QAction("&Reset", self)
        actionReset.setIcon(QIcon("/usr/share/icons/gnome/32x32/actions/reload.png"))
        actionReset.setShortcut("Ctrl-R")
        self.connect(actionReset, SIGNAL("triggered()"), self.reset)

        actionSave = QAction("&Sauver", self)
        actionSave.setIcon(QIcon("/usr/share/icons/gnome/32x32/actions/gtk-save.png"))
        actionSave.setShortcut("Ctrl-S")
        self.connect(actionSave, SIGNAL("triggered()"), self.save)

        actionTerm = QAction("&Terminal", self)
        actionTerm.setIcon(QIcon("/usr/share/icons/gnome/32x32/apps/terminal.png"))
        actionTerm.setShortcut("Ctrl-T")
        self.connect(actionTerm, SIGNAL("triggered()"), self.terminal)

        actionHelp = QAction("&Aide", self)
        actionHelp.setIcon(QIcon("/usr/share/icons/gnome/32x32/actions/help.png"))
        actionHelp.setShortcut("F1")
        self.connect(actionHelp, SIGNAL("triggered()"), self.help)

        #self.toolbar.addWidget(QSpacerItem(0,0))
        actionQuit = QAction("&Quitter", self)
        actionQuit.setIcon(QIcon("/usr/share/icons/gnome/32x32/actions/gtk-quit.png"))
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

        #self.connect(self.list, SIGNAL("itemSelectionChanged()"), self.selectModule)
        #self.connect(self.list, SIGNAL("entered(QModelIndex)"), self.selectModule)
        #self.connect(self.list, SIGNAL("clicked(QModelIndex)"), self.selectModule)
        self.connect(self.list.selectionModel(), SIGNAL("selectionChanged(QItemSelection,QItemSelection)"), self.selectModule)

        # Working but without selection
        #self.connect(self.list, SIGNAL("pressed(QModelIndex)"), self.selectModule)

    def selectModule(self, selected, deselected):
        #mod = self.list.selectedIndexes()[0].data(Qt.UserRole).toPyObject()
        #mod = self.list.currentIndex().data(Qt.UserRole).toPyObject()
        for i in selected.indexes():
            mod = i.data(Qt.UserRole).toPyObject()
            if not mod.selected :
                self.mods[mod.name].select(True)
                action = "Selection"
                self.info.setText(mod.help())
                self.history.append("%s du module %s (version %s)" % (action, mod.name, mod.default_version) )
                #i.setCheckState(Qt.Checked)

        for i in deselected.indexes():
            mod = i.data(Qt.UserRole).toPyObject()
            if mod.selected :
                self.mods[mod.name].select(False)
                action = "Deselection"
                self.history.append("%s du module %s (version %s)" % (action, mod.name, mod.default_version) )

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
        self.modulesModel.setHorizontalHeaderLabels(["Modules", "Version", "Description"])
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
        QMessageBox.information(self, u"Sauvegarde des modules", "Liste des modules à sauver :\n%s" % msg)
        cea_module = Modulecmd()
        cea_module.save(self.mods)

    def reset(self):
        cea_module = Modulecmd()
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
        self.toolbar.setGeometry(settings.value("geometry", self.toolbar.geometry()).toRect())
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
        self.connect(combo, SIGNAL("currentIndexChanged(int)"), self, SLOT("currentIndexChanged()"))
        combo.setStyleSheet("QComboBox { background-color: #FFFFFF; }");
        return combo

    def setModelData(self, editor, model, index):
        model.setData(index, editor.itemData(editor.currentIndex()))

    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

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
    gui = MoGui(cea_module.mods)
    gui.setModules(cea_module.mods)
    gui.show()

    sys.exit(app.exec_())

