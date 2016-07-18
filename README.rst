PyAuth
======

.. image:: https://img.shields.io/pypi/v/PyAuth.png
    :target: https://pypi.python.org/pypi/PyAuth/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/PyAuth.png
    :target: https://pypi.python.org/pypi/PyAuth/
    :alt: Latest Version
    
.. image:: https://img.shields.io/github/release/tknarr/PyAuth.png
    :target: https://github.com/tknarr/PyAuth/releases/latest
    :alt: Latest Version

Copyright 2016 Todd T Knarr <tknarr@silverglass.org>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. The Fernet AES256 implementation (fernet256.py) is dual licensed
under the terms of the Apache License version 2.0 and the BSD License as
noted in the source file.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License (included in
LICENSE.html) for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see `http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_

Summary
-------

PyAuth is a two-factor authentication program compatible with Google Authenticator
and other software and hardware using the standard TOTP algorithm outlined in
`RFC 6238 <https://tools.ietf.org/html/rfc6238>`_ (support for the HOTP algorithm
outlined in `RFC 4226 <https://tools.ietf.org/html/rfc4226>`_ is planned).

Secrets are encrypted using AES256, there is no option for storing unencrypted
secrets. If you were using an older beta version, you will be prompted for a
password and the stored secrets will be migrated to the current encryption without
requiring any more user intervention.

PyPI page: `https://pypi.python.org/pypi/PyAuth <https://pypi.python.org/pypi/PyAuth>`_


Prerequisites
-------------

* `wxPython <http://www.wxpython.org/>`_ 3.0 or higher, which requires matching
  `wxWidgets <http://www.wxwidgets.org/>`_
* `pyotp 2.0.1 <https://pypi.python.org/pypi/pyotp>`_ or higher
* `cryptography 1.3 <https://pypi.python.org/pypi/cryptography>`_ or higher
* `pycrypto 2.6.1 <https://pypi/python.org/pypi/pycrypto>`_ or higher, strictly for
  decrypting older databases

wxPython isn't automatically pulled in by ``pip`` because the version at PyPI is
still 2.9. Your distribution probably includes a pre-packaged version, or you can
download it directly from the wxPython web site.

Developers
----------

See the
`Branches page of the project Wiki on GitHub <https://github.com/tknarr/PyAuth/wiki/Branches>`_
for details on which branches are used for what and which ones you should pull from. The
project follows the Git Flow branching scheme.

Status
------

Everything in the v0.0.x series is a development version. v0.0.1 includes the
minimal functionality to be usable. The commit messages up to this point aren't
too useful.

Basic functionality (listed in TODO.md) will get added as versions v0.1.x
through v0.4.x. v0.5.0 is expected to have all functionality checked and
working with the possible exception of the help system. Once I've made sure
any loose ends are taken care of, the version will jump to v0.9.x for
testing. v1.0.0 is planned to be a stable release ready for normal use. The
enhancements listed in TODO.md will occur after v1.0.0 is released.

Known areas of concern
----------------------

Currently the TOTP implementation is coded to use a 30-second time period
compatible with Google Authenticator. Future work will include allowing for
different time periods.

Usage
-----

Command line:

``PyAuth [-n] [-s] [-m] [--icons=(white|grey|dark|transparent)] [--logfile FILENAME] [--no-logfile] [--loglevel (debug|info|warning|error|critical)]``

* ``-s`` enables use of the notification (systray) icon if possible.

* ``-m`` acts as ``-s`` plus hides the main window on startup (minimized to systray).

* ``-n`` forces the program to display in a normal window without using the
  notification icon. This overrides ``-s`` and ``-m`` and any remembered settings
  for the notification icon.
    
* ``--icons`` selects a set of icons with the named background (default white).

* ``--logfile`` allows you to set a log file for errors and messages logged by
  the program. Errors always appear on the console regardless. You may use variable
  and user expansions in the filename.

* ``--no-logfile`` suppresses the log file completely.

* ``--loglevel`` sets the level of log messages to output to the log file.

* ``--version`` requests that the program print out it's version number.

* ``--help`` requests help on the command-line syntax.

The GUI interface should be fairly straightforward at this point. Each entry
is displayed in a pane in a scrolling list showing the service provider and
account, the current OTP (Google Authenticator) code and a timer bar counting
down the time to the next code.

Clicking on an entry selects it. If codes are being masked, selecting an entry
also unmasks it's code while it's selected. Clicking on a selected entry
deselects it. Double-clicking on an entry selects it and copies the current
code for it to the clipboard. The toolbar contains a tool for copying the
code of the currently-selected entry to the clipboard, and tools to move the
currently-selected entry up and down in the list so you can order entries the
way you want them. Right-clicking on an item brings up a context menu to let
you copy the provisioning URI for the entry to the clipboard or display the
QR code representation of the provisioning URI for scanning into another
authenticator app.

When you run PyAuth with an empty database of authentication entries, it'll
display a single dummy entry with a fake code that won't change. The first new
real entry you create will replace it. If you select and edit it, you'll be
given the new-entry dialog instead and your new entry will replace the dummy
one.

In the View menu are options for showing/hiding the toolbar, putting an icon
in the system notification area (systray), showing the timer bars and masking
codes for unselected entries. If the notification icon is visible, the
minimize button on the window frame is removed as you can simply close the
window and leave the notification icon. Clicking the notification icon toggles
the main window off and on. Right-clicking the notification icon brings up a
menu with the option to completely exit the program.

When using the notification icon, the program will not appear in the taskbar
list of active applications. When starting minimized and using the
notification icon, the program's window will initially be hidden and can be
shown by clicking the notification icon. When starting minimized without using
the notification icon, the program will start with it's window shown and
minimized.
