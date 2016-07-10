# PyAuth version history:

* 1.0.0 - Initial release

* 0.9.10 - Implement authenticated 256-bit encryption

* 0.9.7 - Keyboard accelerators working

* 0.9.6 - Fix bug with initial shown/minimized state

* 0.9.5 - Bugfixes

* 0.9.4 - Database encryption
  - Secrets are now encrypted in the database.
  - Docstrings filled in.

* 0.9.3 - Removed post-install creation of .desktop file
  - Post-install scripts just aren't working, so the template's been replaced by a filled-in
    version the user can edit.

* 0.9.2 - Second beta version
  - Version number bump to avoid a collision on PyPI
  - Fixed a bug with paths when generating the .desktop file during post-install

* 0.9.1 - Second beta version
  - Packaging changes, now supports editable install
  - Uses pkg_resources to locate data files
  - Support 8-digit authentication codes
  - Fix window sizing glitches

* 0.9.0 - Ready for beta testing
  - Post-install updates PyAuth.desktop from PyAuth.desktop.in replacing variables
    with paths from sysconfig
  - Final Python 3 compatibility changes

* 0.6.2 - Packaging of icons and desktop shortcut file

* 0.6.1 - Full license text in separate dialog
  - Fix bug in instance-already-running test
  - Add item to show the full license text to the help menu
  - Python 3 compatibility changes

* 0.6.0 - Logging and packaging
  - Improve logging, log to file as well as console
  - Package for PyPI/pip

* 0.5.0 - Cleanup, first alpha

* 0.4.4 - Single-instance via lockfile

* 0.4.3 - Add redirection of logging to a file

* 0.4.2 - Additional database file saves

* 0.4.1 - Bug fixes

* 0.4.0 - Notification/systray icon, icons

* 0.3.2 - Got sizing working when the toolbar's shown or hidden. Messy.

* 0.3.1 - Fix problem with pyOTP and base32 padding of secrets

* 0.3.0 - Code mostly working

* 0.0.1 - Basic UI and functionality
