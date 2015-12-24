# PyAuth to-do list

* Basic functionality:
  - Toolbar for main frame
  - Select entry via keyboard
  - Move entries up/down
  - Show/hide timers
  - Show/hide all codes
  - Click to show/hide code when all codes hidden
  - Help system
  - Menu accelerators
  - Add icon to About dialog and for system use
  - Minimize to the systray
  - Start minimized, including starting minimized to the systray
* Enhancements:
  - Pegging the window position relative to a corner of the screen so
    it maintains that relative position as the screen size changes. That'd
    also include automatically reducing the vertical size to keep the
    entirety of the window on-screen when it opens.
  - Subclass authentication entry classes and panels
  - HOTP entries and code generation
  - Change databases
  - Read QR codes
  - Generate QR codes
  - Import/export databases:
    - CSV file
    - WinAuth
    - JAuth
    - Google sqlite3
  - Fonts and colors:
    - Application
    - Entry panel
    - Label area
    - Code area
    - Timer gauge
