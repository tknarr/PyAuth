# -*- coding: utf-8 -*-
"""Frame for the main window."""

## PyAuth - Google Authenticator desktop application
## Copyright (C) 2016 Todd T Knarr <tknarr@silverglass.org>

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see http://www.gnu.org/licenses/

import math
import wx

import Configuration
import pkg_resources
from About import GetAboutInfo, GetIconBundle, GetTaskbarIcon
from AuthEntryPanel import AuthEntryPanel
from AuthenticationStore import AuthenticationStore
from ChangeDatabasePasswordDialog import ChangeDatabasePasswordDialog
from DatabasePasswordDialog import DatabasePasswordDialog
from Errors import DecryptionError, PasswordError
from HTMLTextDialog import HTMLTextDialog
from Logging import GetLogger
from NewEntryDialog import NewEntryDialog
from UpdateEntryDialog import UpdateEntryDialog


class AuthTaskbarIcon(wx.TaskBarIcon):
    """Notification tray icon."""

    def __init__(self, frame, icon):
        """Initialize the icon."""
        wx.TaskBarIcon.__init__(self)

        self.frame = frame
        self.icon = icon

        # Find out our icon size and set the appropriate icon from our bundle
        self.SetIcon(self.icon, "PyAuth OTP")

        # Popup menu actions
        self.Bind(wx.EVT_MENU, self.OnMenuExit, id = wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, id = wx.ID_ABOUT)
        # Double-click on taskbar icon toggles window shown/hidden, handled by frame
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.frame.OnTaskbarDClick)

        GetLogger().debug("TBI init done")

    def CreatePopupMenu(self):
        """Create the pop-up menu when needed."""
        GetLogger().debug("TBI popup menu created")
        menu = wx.Menu()
        menu.Append(wx.ID_ABOUT, "About", "About PyAuth")
        menu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        return menu

    def OnMenuAbout(self, event):
        """Display the About dialog box."""
        GetLogger().debug("TBI menu about")
        info = GetAboutInfo(wx.ClientDC(self.frame))
        wx.AboutBox(info)

    def OnMenuExit(self, event):
        """Exit the program."""
        GetLogger().debug("TBI menu exit")
        # Pass this on to the frame as a forced-close operation
        self.frame.Close(True)


class AuthFrame(wx.Frame):
    """Frame for the main window."""

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr,
                 initial_systray = None, initial_minimized = None, iconset = None):
        """Initialize the parts of the frame that can be initialized before window creation."""

        # Flag so we don't save anything if the user asked us to abort in the face
        # of a lockfile problem.
        self.do_not_save = False
        # Flag indicating we were actually shown on the display
        self.displayed = False

        # We need to set up a few things before we know the style flags we should use
        # Our current icon set's the one specified on the command line, or the configured
        # set. The command line option doesn't change the configured set.
        self.configured_icon_set = Configuration.GetIconSet()
        self.icon_set = Configuration.GetIconSet()
        if iconset != None:  # Command line option overrides config
            self.icon_set = iconset
        GetLogger().debug("Icon bundle %s selected", self.icon_set)
        self.icon_bundle = GetIconBundle(self.icon_set)
        if self.icon_bundle == None:  # Fall back to white
            GetLogger().debug("Icon bundle %s failed, trying white", self.icon_set)
            self.icon_bundle = GetIconBundle('white')
        self.use_systray_icon = Configuration.GetUseTaskbarIcon()
        if initial_systray != None:
            self.use_systray_icon = initial_systray
        self.start_minimized = Configuration.GetStartMinimized()
        if initial_minimized != None:
            self.start_minimized = initial_minimized
        # No maximize button, and no minimize button if we're using the systray icon
        my_style = style & ~wx.MAXIMIZE_BOX
        if self.use_systray_icon and self.icon_bundle != None and wx.TaskBarIcon.IsAvailable():
            my_style = my_style & ~wx.MINIMIZE_BOX

        wx.Frame.__init__(self, parent, id, title, pos, size, my_style, name)
        GetLogger().debug("AF init")

        if self.icon_bundle != None:
            self.SetIcons(self.icon_bundle)

        self.entries_window = None
        self.auth_store = None
        self.entry_panels = []
        self.visible_entries = Configuration.GetNumberOfItemsShown()
        GetLogger().info("Visible entries: %d", self.visible_entries)
        self.entry_height = 0  # Height of tallest panel
        self.entry_width = 0  # Width of widest panel

        # Internal values
        self.entry_border = 2
        self.scrollbar_width = 0
        self.selected_panel = None
        self.show_timers = Configuration.GetShowTimers()
        self.show_all_codes = Configuration.GetShowAllCodes()
        self.show_toolbar = Configuration.GetShowToolbar()
        self.taskbar_icon = None
        self.idle_output = False  # Set True to enable size output during idle events

        self.toolbar = None
        self.tool_ids = {}
        self.toolbar_icon_size = Configuration.GetToolIconSize()
        self.toolbar_height = Configuration.GetToolbarHeight()
        self.toolbar_button_height = 0

        self.password_dialog = None
        self.change_password_dialog = None
        self.new_entry_dialog = None
        self.update_entry_dialog = None
        self.license_dialog = None
        self.license_source = None
        self.since_idle = wx.GetUTCTime()

        # Timers are scarce on some platforms, so we set one up here and broadcast the
        # resulting timer event to all our entry panels for processing. That also simplifies
        # shutdown. The timer will tick roughly once per second. The higher the precision the
        # better, but since we're using absolute times to generate codes rather than counting
        # ticks the precision isn't horribly critical beyond being good enough to keep the UI
        # from being too far out-of-sync with the wall clock second hand.
        self.timer = wx.Timer(self)
        # Start off iconized so timer ticks don't modify controls before they exist. We'll
        # set this to our actual state in OnCreate()
        self.iconized = True

        # Set up the taskbar icon if we're supposed to use it and can (have icons and
        # it's available).
        self.taskbar_icon_image = GetTaskbarIcon('transparent')
        if self.use_systray_icon and self.taskbar_icon_image != None and wx.TaskBarIcon.IsAvailable():
            GetLogger().debug("AF creating taskbar icon")
            self.taskbar_icon = AuthTaskbarIcon(self, self.taskbar_icon_image)
        # If we're in the systray and not starting minimized, don't show us in
        # the taskbar.
        if self.taskbar_icon != None and not self.start_minimized:
            window_style = self.GetWindowStyle()
            self.SetWindowStyle(window_style | wx.FRAME_NO_TASKBAR)

        # Basic window event handlers
        self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCreate(self, event):
        """
        Finish initialization once the window exists.

        This portion of initialization has to be deferred because it will involve
        displaying a password dialog box, which can't happen until the window exists
        and the event loop is running.
        """
        self.Unbind(wx.EVT_WINDOW_CREATE)
        GetLogger().debug("AF created")

        # Prompt for password and create authentication store
        password = ''
        authentication_store_ok = False
        retry = True
        while retry:
            if self.password_dialog == None:
                self.password_dialog = DatabasePasswordDialog(self, wx.ID_ANY, "Database Password")
            self.password_dialog.Reset()
            if self.change_password_dialog == None:
                self.change_password_dialog = ChangeDatabasePasswordDialog(self, wx.ID_ANY, "Database Password")
            self.change_password_dialog.Reset()
            if AuthenticationStore.IsEncryptionActive(Configuration.GetDatabaseFilename()):
                dlg = self.password_dialog
            else:
                dlg = self.change_password_dialog
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                password = dlg.GetPasswordValue()
            else:
                authentication_store_ok = False
                break
            try:
                self.auth_store = AuthenticationStore(Configuration.GetDatabaseFilename(), password)
            except DecryptionError as e:
                GetLogger().error(str(e))
                GetLogger().error("Failure decrypting database.")
                retry = True
            except PasswordError as e:
                GetLogger().error(str(e))
                GetLogger().error("Password problem decrypting database.")
                retry = True
            except Exception as e:
                GetLogger().error(str(e))
                GetLogger().critical("Unexpected exception decrypting database.")
                retry = False
            finally:
                if self.auth_store != None:
                    authentication_store_ok = True
                    retry = False
        if not authentication_store_ok:
            GetLogger().critical("Database could not be opened")
            self.do_not_save = True
            self.Close(True)
            return None

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        menu_bar = self.create_menu_bar()
        self.SetMenuBar(menu_bar)
        self.toolbar = self.create_toolbar()
        self.set_toolbar_state(self.show_toolbar)
        self.entries_window = self.create_entries_window()
        self.GetSizer().Add(self.entries_window, 1, wx.EXPAND, 0)

        # Get scrollbar width so we can account for it in window sizing
        # Turns out for layout we don't need to adjust for this
        self.scrollbar_width = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X, self.entries_window)
        GetLogger().debug("AF scrollbar width = %d", self.scrollbar_width)

        self.populate_entries_window()

        # Window event handlers
        self.entries_window.Bind(wx.EVT_SIZE, self.OnEntryWindowSize)
        self.toolbar.Bind(wx.EVT_SIZE, self.OnToolbarSize)
        self.toolbar.Bind(wx.EVT_SHOW, self.OnToolbarShow)
        self.Bind(wx.EVT_TIMER, self.OnTimerTick)
        self.Bind(wx.EVT_ICONIZE, self.OnIconize)
        self.Bind(wx.EVT_SHOW, self.OnShow)
        if self.idle_output:
            self.Bind(wx.EVT_IDLE, self.OnIdle)
        # Menu event handlers
        self.Bind(wx.EVT_MENU, self.OnMenuNewEntry, id = wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnMenuReindex, id = self.MENU_REINDEX)
        self.Bind(wx.EVT_MENU, self.OnMenuRegroup, id = self.MENU_REGROUP)
        self.Bind(wx.EVT_MENU, self.OnMenuExportProvisioningUris, id = self.MENU_EXPORT_PROVISIONING_URIS)
        self.Bind(wx.EVT_MENU, self.OnMenuQuit, id = wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnMenuCopyCode, id = self.MENU_COPY_CODE)
        self.Bind(wx.EVT_MENU, self.OnMenuEditEntry, id = wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.OnMenuDeleteEntry, id = wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveUp, id = wx.ID_UP)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveDown, id = wx.ID_DOWN)
        self.Bind(wx.EVT_MENU, self.OnMenuShowTimers, id = self.MENU_SHOW_TIMERS)
        self.Bind(wx.EVT_MENU, self.OnMenuShowAllCodes, id = self.MENU_SHOW_ALL_CODES)
        self.Bind(wx.EVT_MENU, self.OnMenuShowToolbar, id = self.MENU_SHOW_TOOLBAR)
        self.Bind(wx.EVT_MENU, self.OnMenuUseSystray, id = self.MENU_SHOW_TRAYICON)
        self.Bind(wx.EVT_MENU, self.OnMenuHelpContents, id = wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnMenuLicense, id = self.MENU_LICENSE)
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, id = wx.ID_ABOUT)
        # Any toolbar tool handlers that aren't also menu item handlers go below here

        self.iconized = self.IsIconized()
        self.timer.Start(1000)
        self.record_toolbar_height()

    def OnEntryWindowSize(self, event):
        """React to resizing of the entries window."""
        GetLogger().debug("OnSize event on entries window")
        self.visible_entries = self.CalcItemsShown()
        GetLogger().debug("OnSize entries window done")

    def OnToolbarSize(self, event):
        """React to resizing of the toolbar."""
        GetLogger().debug("OnSize event on toolbar")
        GetLogger().debug("Toolbar size: %s", self.toolbar.GetSize())
        GetLogger().debug("OnSize event on toolbar done")

    def OnToolbarShow(self, event):
        """React to show/hide of the toolbar."""
        GetLogger().debug("OnShow event on toolbar: %s", "SHOW" if event.IsShown() else "HIDE")
        GetLogger().debug("Toolbar size: %s", self.toolbar.GetSize())
        GetLogger().debug("OnShow event on toolbar done")

    def OnTimerTick(self, event):
        """
        React to timer ticks.

        Insures timer ticks are not broadcast after shutdown begins or while
        minimized (entry panels don't need to update while not visible).
        """
        if self.timer != None and not self.iconized:
            # Broadcast the event to all entry panels for processing
            for panel in self.entry_panels:
                panel.QueueEvent(event.Clone())

    def OnIdle(self, event):
        """
        React to idle events.

        The only thing occurring during idle events is regular logging of the sizes and
        states of selected windows to aid debugging sizing-related issues. The idle event
        won't be bound to this method when the idle_output flag is set False, so normally
        this method won't be called in production releases.
        """
        if self.idle_output:
            now = wx.GetUTCTime()
            t = now - self.since_idle
            if t > 10:
                self.since_idle = now
                GetLogger().debug("IDLE FR window size %s min %s",
                                  self.GetSize(), self.GetMinSize())
                GetLogger().debug("IDLE FR client size %s min %s",
                                  self.GetClientSize(), self.GetMinClientSize())
                GetLogger().debug("IDLE EW window size %s min %s",
                                  self.entries_window.GetSize(), self.entries_window.GetMinSize())
                GetLogger().debug("IDLE EW client size %s min %s",
                                  self.entries_window.GetClientSize(), self.entries_window.GetMinClientSize())
                GetLogger().debug("IDLE toolbar size %s", self.toolbar.GetSize().GetHeight())
                GetLogger().debug("IDLE tool size %s", self.toolbar.GetToolSize())

    def OnIconize(self, event):
        """
        React to being iconified or restored.

        When restored it forces an immediate update of the countdown timer bars in the
        entry panels and a refresh of their current code display.
        """
        was_iconized = self.iconized
        self.iconized = event.IsIconized()
        if was_iconized and not self.iconized:
            # Broadcast the event to all entry panels for processing
            for panel in self.entry_panels:
                panel.UpdateTimerGauge()
        event.Skip()

    def OnShow(self, event):
        """
        React to the window being shown.

        Needed so that the window-close code can tell whether the window was ever shown
        or not. If it was never shown, saving of the last window size will be skipped
        because the size may never have been set.
        """
        if event.IsShown():
            self.displayed = True
        event.Skip()

    def OnKey(self, event):
        """Process a keypress event."""
        key = event.GetUnicodeKey()
        if key == wx.WXK_NONE:
            key = event.GetKeyCode()
        GetLogger().debug("AF OnKey code %d", key)
        # The Escape key deselects any selected entry
        if key == wx.WXK_ESCAPE:
            if self.selected_panel != None:
                self.selected_panel.Deselect()
                self.selected_panel = None
        elif key == wx.WXK_UP or key == wx.WXK_DOWN or key == wx.WXK_NUMPAD_UP or key == wx.WXK_NUMPAD_UP:
            if not event.HasModifiers():
                # Alone, Up/Down arrow keys change the selected panel
                if self.selected_panel == None:
                    i = 0
                else:
                    i = self.entry_panels.index(self.selected_panel)
                    if key == wx.WXK_UP or key == wx.WXK_NUMPAD_UP:
                        if i > 0:
                            i -= 1
                    elif key == wx.WXK_DOWN or key == wx.WXK_NUMPAD_DOWN:
                        if i < len(self.entry_panels) - 1:
                            i += 1
                    self.selected_panel.Deselect()
                self.selected_panel = self.entry_panels[i]
                self.selected_panel.Select()
                # Scroll to make selected panel visible
                x, y = self.entries_window.GetViewStart().Get()
                if i <= y:
                    self.entries_window.Scroll(0, i)
                elif i >= y + self.visible_entries:
                    self.entries_window.Scroll(0, i - self.visible_entries + 1)
        else:
            event.Skip()

    def OnCloseWindow(self, event):
        """
        React to the window being closed.

        If using the notification tray icon and the close event can be vetoed, it will
        be vetoed and converted into hiding the window instead. This makes the close
        button act like minimize-to-notificat-tray. If the close event can't be vetoed
        or the notification tray icon isn't in use, the normal shutdown code will be
        executed.
        """
        GetLogger().debug("AF close window")
        # If we're using the taskbar icon and not being forced to close, just hide the
        # window and remove it's entry from the taskbar list of active applications.
        if self.taskbar_icon != None and event.CanVeto():
            window_style = self.GetWindowStyle()
            self.SetWindowStyle(window_style | wx.FRAME_NO_TASKBAR)
            self.Hide()
            event.Veto(True)
        else:
            self.timer.Stop()
            self.Unbind(wx.EVT_TIMER)
            self.timer = None
            if not self.do_not_save:
                if self.auth_store != None:
                    try:
                        self.auth_store.Save()
                    except PasswordError:
                        dlg = wx.MessageDialog(self, "A database password is required.", "Error",
                                               style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                        dlg.SetExtendedMessage("The database could not be properly saved.")
                        dlg.ShowModal()
                        dlg.Destroy()
                wp = self.GetPosition()
                Configuration.SetLastWindowPosition(wp)
                if self.displayed:
                    ws = self.GetSize()
                    Configuration.SetLastWindowSize(ws)
                ## GetLogger().debug( "AF entries window size = %s, min = %s", self.entries_window.GetSize(),
                ##                    self.entries_window.GetMinSize() )
                ## GetLogger().debug( "AF window client size = %s, min = %s", self.GetClientSize(),
                ##                    self.GetMinClientSize() )
                self.visible_entries = self.CalcItemsShown()
                GetLogger().info("Items visible: %d", self.visible_entries)
                Configuration.SetNumberOfItemsShown(self.visible_entries)
                Configuration.SetShowTimers(self.show_timers)
                Configuration.SetShowAllCodes(self.show_all_codes)
                Configuration.SetShowToolbar(self.show_toolbar)
                Configuration.SetToolbarHeight(self.toolbar_height)
                Configuration.SetUseTaskbarIcon(self.use_systray_icon)
                Configuration.SetStartMinimized(self.start_minimized)
                Configuration.SetIconSet(self.configured_icon_set)
                Configuration.Save()
            if self.license_dialog != None:
                self.license_dialog.Destroy()
            if self.new_entry_dialog != None:
                self.new_entry_dialog.Destroy()
            if self.update_entry_dialog != None:
                self.update_entry_dialog.Destroy()
            if self.change_password_dialog != None:
                self.change_password_dialog.Destroy()
            if self.password_dialog != None:
                self.password_dialog.Destroy()
            if self.taskbar_icon != None:
                self.taskbar_icon.Destroy()
            self.Destroy()

    def OnTaskbarDClick(self, event):
        """React to the notification tray icon being double-clicked."""
        if self.IsShown():
            GetLogger().debug("AF taskbar clicked Hide")
            window_style = self.GetWindowStyle()
            self.SetWindowStyle(window_style | wx.FRAME_NO_TASKBAR)
            self.Hide()
        else:
            GetLogger().debug("AF taskbar clicked Show")
            window_style = self.GetWindowStyle()
            self.SetWindowStyle(window_style & ~wx.FRAME_NO_TASKBAR)
            self.Show()

    def OnMenuQuit(self, event):
        """React to the Quit menu command by closing the window."""
        GetLogger().debug("AF menu Quit command")
        self.Close(True)

    def OnMenuNewEntry(self, event):
        """Handle creating a new authentication entry via the menu or toolbar."""
        GetLogger().debug("AF menu New Entry command")
        if self.new_entry_dialog == None:
            self.new_entry_dialog = NewEntryDialog(self, wx.ID_ANY, "New Entry")
        self.new_entry_dialog.Reset()

        result = self.new_entry_dialog.ShowModal()
        if result == wx.ID_OK:
            GetLogger().debug("AF NE creating new entry")
            provider = self.new_entry_dialog.GetProviderValue()
            account = self.new_entry_dialog.GetAccountValue()
            secret = self.new_entry_dialog.GetSecretValue()
            digits = self.new_entry_dialog.GetDigitsValue()
            original_label = self.new_entry_dialog.GetOriginalLabel()
            if original_label == '':
                original_label = provider + ':' + account
            GetLogger().debug("AF NE provider %s", provider)
            GetLogger().debug("AF NE account  %s", account)
            GetLogger().debug("AF NE digits   %d", digits)
            GetLogger().debug("AF NE orig lbl %s", original_label)
            try:
                entry = self.auth_store.Add(provider, account, secret, digits, original_label)
                sts = ''
            except PasswordError:
                entry = None
                sts = 'password'
            if entry != None:
                GetLogger().debug("AF NE new panel: %d", entry.GetGroup())
                # If all we have is the dummy entry then replace it, otherwise add the new entry at the end
                if len(self.entry_panels) == 1 and self.entry_panels[0].GetEntry() == None:
                    panel = self.entry_panels[0]
                    panel.SetEntry(entry)
                    GetLogger().debug("AF NE replaced dummy panel with: %s", panel.GetName())
                else:
                    panel = AuthEntryPanel(self.entries_window, wx.ID_ANY, style = wx.BORDER_THEME,
                                           entry = entry, code_max_digits = self.auth_store.MaxDigits())
                    panel.MaskCode(not self.show_all_codes)
                    panel.ShowTimer(self.show_timers)
                    self.entry_panels.append(panel)
                    GetLogger().debug("AF NE add panel: %s", panel.GetName())
                    self.entries_window.GetSizer().Add(panel, 0, wx.ALL | wx.ALIGN_LEFT,
                                                       self.entry_border)
                ## GetLogger().debug( "AF NE panel size %s min %s", unicode( panel.GetSize() ),
                ##                    unicode( panel.GetMinSize() ) )
                self.UpdatePanelSize()
            else:
                if sts == 'password':
                    GetLogger().debug("AF NE password error")
                    dlg = wx.MessageDialog(self, "A database password is required.", "Error",
                                           style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                else:
                    GetLogger().debug("AF NE duplicate item")
                    dlg = wx.MessageDialog(self, "That entry already exists.", "Error",
                                           style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                    dlg.SetExtendedMessage("Provider: {0}\nAccount: {1}".format(provider, account))
                dlg.ShowModal()
                dlg.Destroy()

    def OnMenuEditEntry(self, event):
        """Handle editing an existing authentication entry via the menu or toolbar."""
        GetLogger().debug("AF menu Edit Entry command")
        if self.update_entry_dialog == None:
            self.update_entry_dialog = UpdateEntryDialog(self, wx.ID_ANY, "Edit Entry")
        entry = None
        if self.selected_panel == None:
            dlg = wx.MessageDialog(self, "No entry selected.", "Error",
                                   style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
            dlg.SetExtendedMessage("You must select an entry to edit.")
            dlg.ShowModal()
            dlg.Destroy()
        else:
            entry = self.selected_panel.GetEntry()
            if entry == None:
                self.OnMenuNewEntry(event)  # Dummy panel selected, create a new entry instead
            else:
                self.update_entry_dialog.Reset(entry.GetProvider(), entry.GetAccount(),
                                               entry.GetSecret(), entry.GetDigits())
                result = self.update_entry_dialog.ShowModal()
                if result == wx.ID_OK:
                    provider = self.update_entry_dialog.GetProviderValue()
                    account = self.update_entry_dialog.GetAccountValue()
                    secret = self.update_entry_dialog.GetSecretValue()
                    digits = self.update_entry_dialog.GetDigitsValue()
                    if provider == entry.GetProvider():
                        provider = None
                    if account == entry.GetAccount():
                        account = None
                    if secret == entry.GetSecret():
                        secret = None
                    if digits == entry.GetDigits():
                        digits = None
                    if provider != None or account != None or secret != None or digits != None:
                        GetLogger().debug("AF UE updating entry")
                        status = self.auth_store.Update(entry.GetGroup(), provider, account, secret, digits)
                        if status < 0:
                            if status == -100:
                                dlg = wx.MessageDialog(self, "A database password is required.", "Error",
                                                       style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                            else:
                                dlg = wx.MessageDialog(self, "Database is corrupted.", "Error",
                                                       style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                                dlg.SetExtendedMessage("Multiple copies of the entry were found.\n" +
                                                       "The database is likely corrupted and needs repaired.")
                            dlg.ShowModal()
                            dlg.Destroy()
                        elif status == 0:
                            dlg = wx.MessageDialog(self, "Entry not found.", "Error",
                                                   style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                            dlg.SetExtendedMessage("The entry was not found in the database.\n" +
                                                   "This should not have happened.")
                            dlg.ShowModal()
                            dlg.Destroy()
                        else:
                            self.selected_panel.ChangeContents()
                            ## GetLogger().debug( "AF UE panel size %s min %s", unicode( panel.GetSize() ),
                            ##                    unicode( panel.GetMinSize() ) )
                            self.UpdatePanelSize()

    def OnMenuDeleteEntry(self, event):
        """Handle deleting an authentication entry via the menu or toolbar."""
        GetLogger().debug("AF menu Delete Entry command")
        if self.selected_panel != None:
            GetLogger().debug("AF DE deleting panel %s", self.selected_panel.GetName())
            panel = self.selected_panel
            panel.ClearBackground()
            self.selected_panel = None
            # Remove the panel from the entries list and the entries window
            self.entry_panels.remove(panel)
            status = self.entries_window.GetSizer().Detach(panel)
            if status:
                # Delete the panel's entry in the authentication store
                entry = panel.GetEntry()
                if entry != None:
                    self.auth_store.Delete(entry.GetGroup())
                panel.Destroy()
                self.entries_window.GetSizer().Layout()
            else:
                GetLogger().warning("Could not remove %s from entries window", panel.GetName())
            ## GetLogger().debug( "AF UE panel size %s min %s", unicode( panel.GetSize() ),
            ##                    unicode( panel.GetMinSize() ) )
            self.UpdatePanelSize()
        else:
            dlg = wx.MessageDialog(self, "No entry selected.", "Error",
                                   style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
            dlg.SetExtendedMessage("You must select an entry to delete.")
            dlg.ShowModal()
            dlg.Destroy()

    def OnMenuCopyCode(self, event):
        """
        Handle copying the current code via the menu or toolbar.

        The current code of the selected entry is copied to the clipboard. If no entry is
        selected an error is reported.
        """
        GetLogger().debug("AF tool CopyCode command")
        if self.selected_panel != None:
            if not self.selected_panel.CopyCodeToClipboard():
                dlg = wx.MessageDialog(self, "Problem copying code to clipboard.", "Error",
                                       style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
                dlg.SetExtendedMessage("An error was encountered copying the code to the clipboard.")
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self, "No entry selected.", "Error",
                                   style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
            dlg.SetExtendedMessage("You must select an entry to copy the code from.")
            dlg.ShowModal()
            dlg.Destroy()

    def OnMenuMoveUp(self, event):
        """Handle moving an authentication entry up one position."""
        ## GetLogger().debug( "AF menu Move Up command" )
        if self.selected_panel != None:
            i = self.entry_panels.index(self.selected_panel)
            if i > 0 and i < len(self.entry_panels):
                ## GetLogger().debug( "AF moving entry %d up", i )
                # Swap the selected panel with the one before it in the list by popping it
                # and inserting it one position before it's previous location, then swap the
                # sort indexes of the two panels we switched around.
                tgt = self.entry_panels.pop(i)
                self.entry_panels.insert(i - 1, tgt)
                si = self.entry_panels[i].GetSortIndex()
                self.entry_panels[i].SetSortIndex(self.entry_panels[i - 1].GetSortIndex())
                self.entry_panels[i - 1].SetSortIndex(si)
                # Then visually update the list by swapping the items in the sizer
                sts = self.entries_window.GetSizer().Remove(i)
                if sts:
                    self.entries_window.GetSizer().Insert(i - 1, tgt, 0, wx.ALL | wx.ALIGN_LEFT,
                                                          self.entry_border)
                    self.SendSizeEvent()
                else:
                    GetLogger().warning("Error removing item %d from entries window. Recovering.", i)
                    self.depopulate_entries_window()
                    self.populate_entries_window()
                    self.UpdatePanelSize()
                # Scroll to make selected panel visible
                x, y = self.entries_window.GetViewStart().Get()
                if i <= y:
                    self.entries_window.Scroll(0, i)
                elif i >= y + self.visible_entries:
                    self.entries_window.Scroll(0, i - self.visible_entries + 1)
            else:
                GetLogger().debug("AF entry %d out-of-range", i)
                wx.Bell()

    def OnMenuMoveDown(self, event):
        """Handle moving an authentication entry down one position."""
        ## GetLogger().debug( "AF menu Move Down command" )
        if self.selected_panel != None:
            i = self.entry_panels.index(self.selected_panel)
            if i >= 0 and i < len(self.entry_panels) - 1:
                ## GetLogger().debug( "AF moving entry %d down", i )
                # Swap the selected panel with the one after it in the list by popping the
                # one after it and inserting that one back at the selected panel's position,
                # then swap the sort indexes of the two panels we switched around.
                tgt = self.entry_panels.pop(i + 1)
                self.entry_panels.insert(i, tgt)
                si = self.entry_panels[i + 1].GetSortIndex()
                self.entry_panels[i + 1].SetSortIndex(self.entry_panels[i].GetSortIndex())
                self.entry_panels[i].SetSortIndex(si)
                # Then visually update the list by swapping the items in the sizer
                sts = self.entries_window.GetSizer().Remove(i + 1)
                if sts:
                    self.entries_window.GetSizer().Insert(i, tgt, 0, wx.ALL | wx.ALIGN_LEFT,
                                                          self.entry_border)
                    self.SendSizeEvent()
                else:
                    GetLogger().warning("Error removing item %d from entries window. Recovering.", i)
                    self.depopulate_entries_window()
                    self.populate_entries_window()
                    self.UpdatePanelSize()
                # Scroll to make selected panel visible
                x, y = self.entries_window.GetViewStart().Get()
                if i <= y:
                    self.entries_window.Scroll(0, i)
                elif i >= y + self.visible_entries:
                    self.entries_window.Scroll(0, i - self.visible_entries + 1)
            else:
                GetLogger().debug("AF entry %d out-of-range", i)
                wx.Bell()

    def OnMenuShowTimers(self, event):
        """Handle showing/hiding timer bars from the menu."""
        GetLogger().debug("AF menu Show Timers command: %s", "Show" if event.IsChecked() else "Hide")
        self.show_timers = event.IsChecked()
        for panel in self.entry_panels:
            panel.ShowTimer(self.show_timers)
        # Panel size will have changed, so do this once after we've changed all
        # panels instead of having each panel notify us individually.
        self.UpdatePanelSize()

    def OnMenuShowAllCodes(self, event):
        """Handle showing/masking all codes from the menu."""
        GetLogger().debug("AF menu Show Codes command: %s", "Show" if event.IsChecked() else "Mask")
        self.show_all_codes = event.IsChecked()
        for panel in self.entry_panels:
            panel.MaskCode(not self.show_all_codes)

    def OnMenuShowToolbar(self, event):
        """Handle showing/hiding the toolbar from the menu."""
        GetLogger().debug("AF menu Show Toolbar command: %s", "Show" if event.IsChecked() else "Hide")
        self.set_toolbar_state(event.IsChecked())
        self.AdjustWindowSizes(toolbar_state_changed = True)

    def OnMenuUseSystray(self, event):
        """Handle using or not using the notification tray icon from the menu."""
        GetLogger().debug("AF menu Tray Icon command: %s", "Use" if event.IsChecked() else "None")
        should_use = event.IsChecked()
        if should_use:
            if self.taskbar_icon == None:
                if self.taskbar_icon_image != None and wx.TaskBarIcon.IsAvailable():
                    GetLogger().debug("AF menu Tray Icon creating taskbar icon")
                    self.taskbar_icon = AuthTaskbarIcon(self, self.taskbar_icon_image)
            self.use_systray_icon = True
        else:
            if self.taskbar_icon != None:
                GetLogger().debug("AF menu Tray Icon removing taskbar icon")
                tbi = self.taskbar_icon
                self.taskbar_icon = None
                tbi.Destroy()
            self.use_systray_icon = False

    def OnMenuHelpContents(self, event):
        """Handle displaying the help system from the menu."""
        # TODO menu handler
        GetLogger().warning("Help Contents")

    def OnMenuLicense(self, event):
        """Handle displaying the license from the menu."""
        GetLogger().debug("AF menu License dialog")
        if self.license_dialog == None:
            self.license_dialog = HTMLTextDialog(self, wx.ID_ANY, "License")
        if self.license_source == None:
            license_source = pkg_resources.resource_string('pyauth', 'LICENSE.html')
        self.license_dialog.SetPage(license_source)
        self.license_dialog.ShowModal()

    def OnMenuAbout(self, event):
        """Handle showing the About dialog from the menu."""
        GetLogger().debug("AF menu About dialog")
        info = GetAboutInfo(wx.ClientDC(self))
        wx.AboutBox(info)

    def OnMenuReindex(self, event):
        """Handle a request to reindex the database from the menu."""
        GetLogger().debug("AF menu Reindex command")
        GetLogger().info("Database reindex ordered")
        try:
            self.auth_store.Reindex()
        except PasswordError:
            dlg = wx.MessageDialog(self, "A database password is required.", "Error",
                                   style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
            dlg.ShowModal()
            dlg.Destroy()
        self.depopulate_entries_window()
        self.populate_entries_window()
        self.UpdatePanelSize()

    def OnMenuRegroup(self, event):
        """Handle a request to re-group the database from the menu."""
        GetLogger().debug("AF menu Regroup command")
        GetLogger().info("Database regroup and reindex ordered")
        try:
            self.auth_store.Regroup()
        except PasswordError:
            dlg = wx.MessageDialog(self, "A database password is required.", "Error",
                                   style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE)
            dlg.ShowModal()
            dlg.Destroy()
        self.depopulate_entries_window()
        self.populate_entries_window()
        self.UpdatePanelSize()

    def OnMenuExportProvisioningUris(self, event):
        """Export provisioning URIs for all entry panels to the clipboard in one block."""
        uri_text = ""
        for panel in self.entry_panels:
            uri_text += panel.GetProvisioningUri() + "\n"
        if wx.TheClipboard.Open():
            if wx.TheClipboard.SetData(wx.TextDataObject(uri_text)):
                wx.TheClipboard.Flush()
            else:
                GetLogger().error("Encountered an error exporting the provisioning URIs to the clipboard.")
            wx.TheClipboard.Close()
        else:
            GetLogger().error("Cannot open clipboard.")

    def create_menu_bar(self):
        """Create and populate the menu bar."""
        GetLogger().debug("AF create menu bar")
        mb = wx.MenuBar()

        # Database maintenance submenu
        db_menu = wx.Menu()
        mi = wx.MenuItem(db_menu, wx.ID_ANY, "Reindex", "Regenerate sort indexes in current order")
        self.MENU_REINDEX = mi.GetId()
        db_menu.AppendItem(mi)
        mi = wx.MenuItem(db_menu, wx.ID_ANY, "Regroup", "Completely compact database in current order")
        self.MENU_REGROUP = mi.GetId()
        db_menu.AppendItem(mi)

        # Export submenu
        export_menu = wx.Menu()
        mi = wx.MenuItem(export_menu, wx.ID_ANY, "Provisioning URIs to clipboard",
                         "Copy all provisioning URIs to the clipboard")
        self.MENU_EXPORT_PROVISIONING_URIS = mi.GetId()
        export_menu.AppendItem(mi)

        # File menu
        menu = wx.Menu()
        menu.Append(wx.ID_NEW, "&New entry\tCtrl-N", "Create a new account entry")
        menu.AppendSeparator()
        menu.AppendSubMenu(db_menu, "DB Maintenance")
        menu.AppendSubMenu(export_menu, "Export")
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, "E&xit\tCtrl-Q", "Exit the program")
        mb.Append(menu, "&File")

        # Edit menu
        menu = wx.Menu()
        mi = wx.MenuItem(menu, wx.ID_ANY, "&Copy code\tCtrl-C", "Copy the current code to clipboard")
        self.MENU_COPY_CODE = mi.GetId()
        mi_icon = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU)
        mi.SetBitmap(mi_icon)
        menu.AppendItem(mi)
        menu.AppendSeparator()
        menu.Append(wx.ID_EDIT, "&Edit\tCtrl-E", "Edit the selected entry")
        menu.Append(wx.ID_DELETE, "Delete", "Delete the selected entry")
        menu.AppendSeparator()
        menu.Append(wx.ID_UP, "Move &Up", "Move the selected entry up one position")
        menu.Append(wx.ID_DOWN, "Move &Down", "Move the selected entry down one position")
        mb.Append(menu, "&Edit")

        # View menu
        menu = wx.Menu()
        mi = wx.MenuItem(menu, wx.ID_ANY, "Toolbar", "Show the toolbar", kind = wx.ITEM_CHECK)
        self.MENU_SHOW_TOOLBAR = mi.GetId()
        menu.AppendItem(mi)
        menu.Check(self.MENU_SHOW_TOOLBAR, self.show_toolbar)
        mi = wx.MenuItem(menu, wx.ID_ANY, "Tray Icon", "Show the system tray icon", kind = wx.ITEM_CHECK)
        self.MENU_SHOW_TRAYICON = mi.GetId()
        menu.AppendItem(mi)
        menu.Check(self.MENU_SHOW_TRAYICON, self.use_systray_icon)
        # NEED CODE select icon set background (white, grey, dark, transparent)
        menu.AppendSeparator()
        mi = wx.MenuItem(menu, wx.ID_ANY, "Timers", "Show timer bars", kind = wx.ITEM_CHECK)
        self.MENU_SHOW_TIMERS = mi.GetId()
        menu.AppendItem(mi)
        menu.Check(self.MENU_SHOW_TIMERS, self.show_timers)
        mi = wx.MenuItem(menu, wx.ID_ANY, "All Codes", "Show codes for all entries", kind = wx.ITEM_CHECK)
        self.MENU_SHOW_ALL_CODES = mi.GetId()
        menu.AppendItem(mi)
        menu.Check(self.MENU_SHOW_ALL_CODES, self.show_all_codes)
        mb.Append(menu, "&View")

        # Help menu
        menu = wx.Menu()
        menu.Append(wx.ID_HELP, "&Help\tCtrl-H", "Help index")
        menu.Enable(wx.ID_HELP, False)  # TODO enable after help implemented
        menu.AppendSeparator()
        mi = wx.MenuItem(menu, wx.ID_ANY, "License", "Show license")
        self.MENU_LICENSE = mi.GetId()
        menu.AppendItem(mi)
        menu.Append(wx.ID_ABOUT, "&About", "About PyAuth")
        mb.Append(menu, "&Help")

        return mb

    def create_toolbar(self):
        """Create and populate the toolbar."""
        GetLogger().debug("AF create toolbar")
        toolbar = self.CreateToolBar(name = 'tool_bar')
        toolbar.SetToolBitmapSize(self.toolbar_icon_size)

        self.tool_ids = {}

        tool_icon = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, self.toolbar_icon_size)
        tool = toolbar.AddTool(self.MENU_COPY_CODE, tool_icon,
                               shortHelpString = "Copy the selected code to clipboard")
        self.tool_ids['COPYCODE'] = tool.GetId()

        toolbar.AddSeparator()

        tool_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, self.toolbar_icon_size)
        tool = toolbar.AddTool(wx.ID_UP, tool_icon,
                               shortHelpString = "Move selected entry up one position")
        self.tool_ids['MOVE_UP'] = tool.GetId()

        tool_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_TOOLBAR, self.toolbar_icon_size)
        tool = toolbar.AddTool(wx.ID_DOWN, tool_icon,
                               shortHelpString = "Move selected entry down one position")
        self.tool_ids['MOVE_DOWN'] = tool.GetId()

        toolbar.Realize()
        ## GetLogger().debug( "AF toolbar initial size %s", toolbar.GetSize() )

        return toolbar

    def set_toolbar_state(self, show):
        """Set the shown/hidden state of the toolbar."""
        ## GetLogger().debug( "AF set toolbar state %s -> %s",
        ##                    "Show" if self.show_toolbar else "Hide",
        ##                    "Show" if show else "Hide" )
        if show:
            self.toolbar.Show()
        else:
            self.toolbar.Hide()
        self.record_toolbar_height()
        self.show_toolbar = show
        ## GetLogger().debug( "AF STS toolbar size %s, button size %s, margin %s",
        ##                    self.toolbar.GetSize(), self.toolbar.GetToolSize(), self.toolbar.GetMargins() )

    def record_toolbar_height(self, code = 'def'):
        """Record the height of the toolbar if it's reasonably valid."""
        changed = False
        if self.toolbar != None:
            ts = self.toolbar.GetToolSize()
            if ts.GetHeight() > self.toolbar_button_height:
                self.toolbar_button_height = ts.GetHeight()
                GetLogger().debug("AF RTH %s new toolbar button height %d", code, self.toolbar_button_height)
            ts = self.toolbar.GetSize()
            if ts.GetHeight() > self.toolbar_height:
                self.toolbar_height = ts.GetHeight()
                if self.toolbar_height > self.toolbar_button_height:
                    changed = True
                    GetLogger().debug("AF RTH %s new toolbar height %d", code, self.toolbar_height)
        return changed

    def create_entries_window(self):
        """Create the scrolled window entries will be displayed in."""
        GetLogger().debug("AF create entries window")
        sw = wx.ScrolledWindow(self, wx.ID_ANY, style = wx.VSCROLL | wx.WANTS_CHARS, name = 'entries_window')
        sw.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT)
        sw.EnableScrolling(False, True)
        sw.DisableKeyboardScrolling()
        sw.SetSizer(wx.BoxSizer(wx.VERTICAL))
        return sw

    def populate_entries_window(self):
        """Populate the entries window with authentication entry panels."""
        GetLogger().debug("AF populating the entries window")
        # Create our entry item panels and put them in the scrollable window
        self.entry_panels = []
        for entry in self.auth_store.EntryList():
            ## GetLogger().debug( "AF create panel: %d", entry.GetGroup() )
            panel = AuthEntryPanel(self.entries_window, wx.ID_ANY, style = wx.BORDER_THEME,
                                   entry = entry, code_max_digits = self.auth_store.MaxDigits())
            panel.MaskCode(not self.show_all_codes)
            panel.ShowTimer(self.show_timers)
            self.entry_panels.append(panel)
        if len(self.entry_panels) > 0:
            # Make sure they're sorted at the start
            keyfunc = lambda x: x.GetSortIndex()
            self.entry_panels.sort(key = keyfunc)
        else:
            # Add dummy entry. We need at least this to be able to size things properly. We'll
            # replace it with the first real entry.
            self.entry_panels.append(AuthEntryPanel(self.entries_window, wx.ID_ANY,
                                                    style = wx.BORDER_THEME,
                                                    code_max_digits = self.auth_store.MaxDigits()))
        for panel in self.entry_panels:
            ## GetLogger().debug( "AF add panel: %d - %s", panel.GetSortIndex(), panel.GetName() )
            ## GetLogger().debug( "AF panel size %s min %s", unicode( panel.GetSize() ), unicode( panel.GetMinSize() ) )
            self.entries_window.GetSizer().Add(panel, 0, wx.ALL | wx.ALIGN_LEFT, self.entry_border)

    def depopulate_entries_window(self):
        """Depopulate the entries window and destroy the entry panels."""
        GetLogger().debug("AF depopulating the entries window")
        # Clear out the entries window sizer and then destroy the individual entry panels
        self.entries_window.GetSizer().Clear(False)
        for panel in self.entry_panels:
            # GetLogger().debug( "AF destroy panel: %s", panel.GetName() )
            panel.Destroy()
        self.entry_panels = []

    def CalcItemsShown(self):
        """
        Calculate the number of entries visible.

        The calculation is based on the height of the entries window and the height of a
        single entry. The calculation rounds the result up so any partially-visible entry
        becomes completely visible.
        """
        if self.entries_window == None:
            return self.visible_entries

        height = self.entries_window.GetSize().GetHeight()
        ## GetLogger().debug( "AF CIS win height = %d, entry height = %d", height, self.entry_height )
        r = self.visible_entries
        if self.entry_height > 0:
            d = self.entry_height + 2 * self.entry_border
            r = math.ceil(float(height) / float(d))
            if r < 1:
                r = 1
                ## GetLogger().debug( "AF CIS result = %d / %d = %d", height, d, r )
        return r

    def AdjustWindowSizes(self, toolbar_state_changed = False):
        """
        Adjust the size of the main frame and entries window.

        The calculation is supposed to result in window sizes that exactly show a certain number
        of entries without any partially-visible entries. This requires taking into account the
        toolbar's height.
        """
        ## GetLogger().debug( "AF AWS entry size:  %dx%d, visible = %d", self.entry_width, self.entry_height,
        ##                    self.visible_entries )
        # Need to adjust this here, it depends on the entry height which may change
        self.entries_window.SetScrollRate(0, self.entry_height + 2 * self.entry_border)

        # Finagle this to keep things consistent whether we start with a scrollbar visible or not
        # Yeah it's weird, but that's how wxWidgets appears to work
        column_width = self.entry_width + 2 * self.entry_border
        if self.visible_entries >= len(self.entry_panels):
            column_width += self.scrollbar_width
        # Figure out the window height and minimum height based on entries
        column_height = self.visible_entries * (self.entry_height + 2 * self.entry_border)
        min_height = self.entry_height + 2 * self.entry_border

        # The size calculations are broken out and made explicit to make sure everything's
        # calculated correctly. We end up not using the client sizes, but we need them
        # as intermediate steps to make sure the frame has a minimum size large enough
        # for it's client area to hold the entries window.

        # Calculate size needed in client area of scrolling entries window
        entries_client_size = wx.Size(column_width, column_height)
        entries_min_client_size = wx.Size(column_width, min_height)
        # Convert the client area size to the entries window size
        entries_size = self.entries_window.ClientToWindowSize(entries_client_size)
        entries_min_size = self.entries_window.ClientToWindowSize(entries_min_client_size)

        # Generate correct frame size to hold the entries window plus toolbar
        frame_size = self.ClientToWindowSize(entries_size)
        frame_min_size = self.ClientToWindowSize(entries_min_size)

        # Compensate for toolbar when changing toolbar visibility
        if toolbar_state_changed and self.toolbar_height > self.toolbar_button_height:
            ## GetLogger().debug( "AF AWS adjusting for toolbar %s", "Shown" if self.show_toolbar else "Hidden" )
            if self.show_toolbar:
                frame_size.SetHeight(frame_size.GetHeight() + self.toolbar_height)
                frame_min_size.SetHeight(frame_min_size.GetHeight() + self.toolbar_height)
            if not self.show_toolbar:
                frame_size.SetHeight(frame_size.GetHeight() - self.toolbar_height)
                frame_min_size.SetHeight(frame_min_size.GetHeight() - self.toolbar_height)

        ## GetLogger().debug( "AF AWS FR window size %s min %s", frame_size, frame_min_size )
        ## GetLogger().debug( "AF AWS EW window size %s min %s", entries_size, entries_min_size )
        ## GetLogger().debug( "AF AWS EW client size %s min %s", entries_client_size, entries_min_client_size )

        # Clear the hints so we can resize the frame freely
        self.SetSizeHints(-1, -1)

        # Set window sizes and minimum sizes for the entries window and the frame
        self.entries_window.SetSize(entries_size)
        self.entries_window.SetMinSize(entries_min_size)
        self.SetMinSize(frame_min_size)
        self.SetSize(frame_size)

        # Set hints so we can't be resized wider and resize in entry increments
        self.SetSizeHints(frame_min_size.GetWidth(), frame_min_size.GetHeight(),
                          maxW = frame_size.GetWidth(),
                          incW = column_width, incH = min_height)

    def AdjustPanelSizes(self):
        """
        Adjust the panels so all their labels are the same width.

        All panels should have their labels set to the width needed by the widest label, so that
        all panels end up being the same total width to make a nice even column.
        """
        ## GetLogger().debug( "AF APS" )
        label_width = 0
        self.entry_width = 0
        self.entry_height = 0
        for entry in self.entry_panels:
            w = entry.GetLabelWidth()
            ## GetLogger().debug( "AF APS %s: label width %d", entry.GetName(), w )
            if w > label_width:
                label_width = w
        ## GetLogger().debug( "AF APS label width %d", label_width )
        for entry in self.entry_panels:
            entry.SizeLabels(label_width)
            s = entry.GetPanelSize()
            ## GetLogger().debug( "AF APS panel %s: size %s", entry.GetName(), s )
            if s.GetWidth() > self.entry_width:
                self.entry_width = s.GetWidth()
            if s.GetHeight() > self.entry_height:
                self.entry_height = s.GetHeight()
                ## GetLogger().debug( "AF APS entry width %d height %d", self.entry_width, self.entry_height )

    def UpdatePanelSize(self):
        """
        Update entry panel sizes.

        First adjusts all panels to an even width, then adjusts the window sizes to exactly show
        the correct number of panels.
        """
        ## GetLogger().debug( "AF UPS" )
        self.AdjustPanelSizes()
        self.AdjustWindowSizes()
        self.SendSizeEvent()

    def SelectPanel(self, panel, selected = True):
        """React to a panel being selected."""
        GetLogger().debug("AF panel %s: %s", panel.GetName(), "select" if selected else "deselect")
        if selected:
            if self.selected_panel != None:
                self.selected_panel.Deselect()
            panel.Select()
            self.selected_panel = panel
        else:
            panel.Deselect()
            if self.selected_panel != None:
                self.selected_panel.Deselect()
            self.selected_panel = None

    def InSystray(self):
        """Report whether the notification tray icon will be in use or not."""
        return self.taskbar_icon != None

    def StartMinimized(self):
        """Report whether we will start minimized or not."""
        return self.start_minimized
