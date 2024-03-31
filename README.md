MoGui, Graphical User Interface for Modules
===========================================

MoGui is a Graphical User Interface (GUI) for Environment Modules. It helps
users selecting modules to load and save module collections.

![A sneak peek of MoGui](https://raw.githubusercontent.com/cea-hpc/mogui/main/doc/sneak_peek.gif)

Features
--------

* View available modules, loaded modules, enabled modulepaths and available
  collections
* Load module when selecting it from the available modules list
* Unload module when deselecting it from the available modules list or double
  clicking it from the loaded modules list
* Purge loaded environment, reset to initial environment and restore *default*
  collection
* Save currently loaded environment into the *default* collection
* When right clicking element, show `help` information of available modules,
  `display` information of loaded modules and content of collections
* Apply any environment change made from MoGui onto the shell session that
  launched the GUI application

Installing MoGui
----------------

Install from git repository:

    $ git clone https://github.com/cea-hpc/mogui.git
    $ cd mogui
    $ pip install .

Install from PyPi:

    $ pip install modules-gui

Using MoGui
-----------

Once installed, a `mogui-setup-env` command is available to initialize `mogui`
in your current shell session. Run the following command depending on your
current shell:

`sh`:

    $ eval "$(mogui-setup-env sh)"

`bash`:

    $ eval "$(mogui-setup-env bash)"

`ksh`:

    $ eval "$(mogui-setup-env ksh)"

`zsh`:

    $ eval "$(mogui-setup-env zsh)"

`csh`:

    $ eval "`mogui-setup-env csh`"

`tcsh`:

    $ eval "`mogui-setup-env tcsh`"

`fish`:

    $ eval mogui-setup-env fish | source -

After this initialization step, a `mogui` shell function will be defined in
your shell session (or a shell alias on `csh`/`tcsh` shells).

    $ mogui

By running this shell function/alias, the GUI will appear. Any environment
change made from the GUI (like loading a module or restoring a collection)
will be applied back into the parent shell session that has invoked the GUI.

Requirements
------------

 * Python >= 3.6
 * PyQt5
 * Modules >= 5.2

Licenses
--------

MoGui is distributed under the GNU General Public License, either version 2 or
(at your option) any later version (GPL v2+). Read the file `COPYING.GPLv2`
for details.

MoGui's icons found in the `mogui/icons/mogui-light/symbolic/actions`
directory are imported from the *Adwaita* icon theme of the *GNOME Project*
(http://www.gnome.org). Icons from the `mogui/icons/mogui-dark/symbolic/actions`
directory are modified version of *Adwaita* icons (color switch). This work is
licenced under the Creative Commons Attribution-Share Alike 3.0 United States
License. Read the file `COPYING-ICONS.CCBYSA3` for details.

Authors
-------

 * Aurélien Cedeyn <aurelien.cedeyn AT cea.fr>
 * Xavier Delaruelle <xavier.delaruelle AT cea.fr>
