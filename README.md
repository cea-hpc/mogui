MoGui, Graphical User Interface for Modules
===========================================

MoGui is a Graphical User Interface (GUI) for Environment Modules. It helps
users selecting modules to load and save module collections.

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

License
-------

MoGui is distributed under the GNU General Public License, either version 2 or
(at your option) any later version (GPL v2+). Read the file `COPYING.GPLv2`
for details.

Authors
-------

 * Aurélien Cedeyn <aurelien.cedeyn AT cea.fr>
 * Xavier Delaruelle <xavier.delaruelle AT cea.fr>
