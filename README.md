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
