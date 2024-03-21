MoGui, Graphical User Interface for Modules
===========================================

MoGui is a Graphical User Interface (GUI) for Environment Modules. It helps
users selecting modules to load and save module collections.

Testing MoGui
-------------

To test `mogui` please source the `setup-env` file corresponding to your
shell kind.

For `sh`, `bash`, `ksh` or `zsh`  shells:

    $ source share/setup-env.sh

For `csh` or `tcsh` shells:

    $ source share/setup-env.csh

For `fish` shell:

    $ source share/setup-env.fish

Then run created `mogui` shell function/alias:

    $ mogui

Requirements
------------

 * Python >= 3.6
 * PyQt5
 * Modules >= 5.2

License
-------

MoGui is distributed under the GNU General Public License, either version 2 or
(at your option) any later version (GPL v2+). Read the file `COPYING.GPLv2`
for details.

Authors
-------

 * Aurélien Cedeyn <aurelien.cedeyn AT cea.fr>
 * Xavier Delaruelle <xavier.delaruelle AT cea.fr>
