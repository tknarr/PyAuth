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
* otpauth package, [https://pypi.python.org/pypi/otpauth/](https://pypi.python.org/pypi/otpauth/)

## Developers

See [the Branches page](https://github.com/tknarr/PyAuth/wiki/Branches) for
which branches are used for what and which ones you should pull from.

## Status

Everything in the v0.0.x series is a development version. v0.0.1 includes the
minimal functionality to be usable. The commit messages up to this point aren't
too useful.

Basic functionality (listed in TODO.md) will get added as v0.1.x. Once that's
complete and it's stable enough for testing, the version will get bumped to
v0.9.x until any final glitches are cleaned up. v1.0.0 will be a hopefully
stable release ready for regular users. I don't intend any of the enhancements
listed in TODO.md to be added until v1.0.0 is done.

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

You can select an entry by clicking on it with the mouse so it's highlighted.
Clicking toggles the selection of the entry on and off, and clicking on one
entry deselects any other selected entries. Currently you can only select one
entry. You can edit or delete an entry by selecting it and using Edit or
Delete from the Edit menu. You can create a new entry using New from the File
menu. The new entry will be added at the bottom of the list.

When you run PyAuth with an empty database of authentication entries, it'll
display a single dummy entry with a fake code that won't change. The first new
real entry you create will replace it. If you select and edit it, you'll be
given the new-entry dialog instead and your new entry will replace the dummy
one.
