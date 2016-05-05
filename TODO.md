# PyAuth to-do list

Future enhancements:

* Switch database to SQLite
* Pegging the window position relative to a corner of the screen so
  it maintains that relative position as the screen size changes. That'd
  also include automatically reducing the vertical size to keep the
  entirety of the window on-screen when it opens.
* Subclass authentication entry classes and panels
* Different intervals for TOTP
* HOTP entries and code generation
* Allow opening of other databases
* Read QR codes
* Generate QR codes
* Import/export databases:
  - CSV file
  - WinAuth
  - JAuth
  - Google sqlite3
* Fonts and colors:
  - Application
  - Entry panel
  - Label area
  - Code area
  - Timer gauge
