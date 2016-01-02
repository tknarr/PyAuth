# PyAuth

### Copyright 2015 Todd T Knarr

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License (included in
LICENSE.md) for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).

## Prerequisites

* wxPython 3.x, which requires matching wxWidgets 3.x
* pyotp 2.0.1 or higher, [https://pypi.python.org/pypi/pyotp](https://pypi.python.org/pypi/pyotp)

## Developers

See [the Branches page](https://github.com/tknarr/PyAuth/wiki/Branches) for
which branches are used for what and which ones you should pull from.

## Status

Everything in the v0.0.x series is a development version. v0.0.1 includes the
minimal functionality to be usable. The commit messages up to this point aren't
too useful.

Basic functionality (listed in TODO.md) will get added as versions v0.1.x
through v0.4.x. v0.5.0 is expected to have all functionality checked and
working with the possible exception of the help system. Once I've made sure
any loose ends are taken care of, the version will jump to v0.9.x for
testing. v1.0.0 is planned to be a stable release ready for normal use. The
enhancements listed in TODO.md will occur after v1.0.0 is released.

#### Known areas of concern

* Encryption of the database. Right now it's a plain wxWidgets configuration
  file with one section per entry. The code sets permissions to keep the file
  readable only by the user themselves. That's problematic on Windows, but I'm
  not really targetting that platform since it's got a good option in
  WinAuth. I'm considering adding encryption to keep the secret strings in the
  database from being easily read by malware, at the cost of having to
  manually enter a password when the program starts.

## Using

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
way you want them

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
