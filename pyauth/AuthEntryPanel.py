# -*- coding: utf-8 -*-
"""Authentication code entry panel."""

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

import wx

from Logging import GetLogger
from QrCode import QrCodeFrame


class AuthEntryPanel(wx.Panel):
    """Authentication code entry panel."""

    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr, entry = None, code_max_digits = 6):
        """
        Initialize the panel.

        Normal initialization includes a reference to the panel's entry in the
        authentication store plus the number of code digits the panel should display.
        Omitting these arguments results in a blank panel.
        """
        wx.Panel.__init__(self, parent, id, pos, size, style | wx.WANTS_CHARS, name)

        self.entry = entry
        self.sort_index = 0
        self.code = ''
        self.code_digits = 6
        self.code_max_digits = code_max_digits
        self.code_mask_char = 'X'
        self.label_width = 0

        self.left_down = False
        self.selected = False
        self.totp_cycle = 0
        self.totp_period = 30
        self.code_masked = False
        self.timers_shown = True

        self.label_panel = None
        self.provider_text = None
        self.account_text = None
        self.code_text = None
        self.timer_gauge = None

        if entry != None:
            self.SetName('entry_panel_{0:d}'.format(self.entry.GetGroup()))
            self.code_digits = self.entry.GetDigits()
        else:
            self.SetName('entry_panel_X')
            self.code_digits = 6
        ## GetLogger().debug( "AEP init %s", self.GetName() )

        # Create panel child controls

        self.provider_font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.account_font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.code_font = wx.Font(28, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        self.label_panel = wx.Panel(self, style = wx.BORDER_NONE | wx.WANTS_CHARS, name = 'label_panel')
        label_sizer = wx.BoxSizer(wx.VERTICAL)
        self.label_panel.SetSizer(label_sizer)

        self.provider_text = wx.StaticText(self.label_panel, wx.ID_ANY, "PROVIDER", style = wx.ALIGN_LEFT,
                                           name = 'provider_text')
        self.provider_text.Wrap(-1)
        self.provider_text.SetFont(self.provider_font)
        self.provider_text.Fit()
        label_sizer.Add(self.provider_text, 1,
                        wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)

        self.account_text = wx.StaticText(self.label_panel, wx.ID_ANY, "ACCOUNT", style = wx.ALIGN_LEFT,
                                          name = 'account_text')
        self.account_text.Wrap(-1)
        self.account_text.SetFont(self.account_font)
        self.account_text.Fit()
        label_sizer.Add(self.account_text, 1,
                        wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)

        self.label_panel.Fit()
        sizer.Add(self.label_panel, 0, wx.EXPAND | wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 2)

        self.code_text = wx.StaticText(self, wx.ID_ANY, self.code_mask_char * self.code_max_digits,
                                       style = wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE,
                                       name = 'code_text')
        self.code_text.Wrap(-1)
        self.code_text.SetFont(self.code_font)
        self.code_text.Fit()
        self.code_text.SetInitialSize(self.code_text.GetSize())
        self.code_text.SetMinSize(self.code_text.GetSize())
        sizer.Add(self.code_text, 0,
                  wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE,
                  12)

        self.totp_period = entry.GetPeriod() if self.entry != None else 30
        self.timer_gauge = wx.Gauge(self, wx.ID_ANY, self.totp_period - 1, size = wx.Size(30, 15),
                                    style = wx.GA_HORIZONTAL, name = 'timer_gauge')
        self.timer_gauge.SetValue(self.totp_period - 1)
        self.timer_gauge.SetMinSize(self.timer_gauge.GetSize())
        sizer.Add(self.timer_gauge, 0, wx.RIGHT | wx.ALIGN_CENTER, 2)

        # Create our context menu
        self.context_menu = wx.Menu()
        item = self.context_menu.Append(wx.ID_ANY, "Copy provisioning URI to clipboard")
        self.Bind(wx.EVT_MENU, self.OnProvisioningUri, item)
        item = self.context_menu.Append(wx.ID_ANY, "Display QR code image")
        self.Bind(wx.EVT_MENU, self.OnQrCodeImage, item)

        self.UpdateContents()

        if entry != None:
            self.code = str(self.entry.GenerateNextCode())

        self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        self.Bind(wx.EVT_TIMER, self.OnTimerTick)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.MouseBind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.MouseBind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.MouseBind(wx.EVT_LEFT_UP, self.OnLeftUp)

        gp = self.GetGrandParent()
        self.Bind(wx.EVT_CHAR, gp.OnKey)
        self.label_panel.Bind(wx.EVT_CHAR, gp.OnKey)
        self.provider_text.Bind(wx.EVT_CHAR, gp.OnKey)
        self.account_text.Bind(wx.EVT_CHAR, gp.OnKey)
        self.code_text.Bind(wx.EVT_CHAR, gp.OnKey)
        self.timer_gauge.Bind(wx.EVT_CHAR, gp.OnKey)

        ## GetLogger().debug( "AEP init done %s", self.GetName() )

    def MouseBind(self, event_type, func):
        """Bind a mouse event."""
        self.Bind(event_type, func)
        self.label_panel.Bind(event_type, func)
        self.provider_text.Bind(event_type, func)
        self.account_text.Bind(event_type, func)
        self.code_text.Bind(event_type, func)

    def __cmp__(self, other):
        """Compare two entries by name."""
        return cmp(self.GetName(), other.GetName()) if other != None else -1

    def OnCreate(self, event):
        """Handle window creation."""
        self.Unbind(wx.EVT_WINDOW_CREATE)
        ## GetLogger().debug( "AEP created" )
        self.ChangeContents()

    def OnTimerTick(self, event):
        """Update the timer countdown bar once per tick."""
        self.UpdateTimerGauge()

    def OnLeftDown(self, event):
        """Handle left-button-down event."""
        self.left_down = True
        event.Skip()

    def OnLeftUp(self, event):
        """
        Handle left-button-up event.

        If preceeded by a left-button-down event, the panel is selected. Otherwise
        the event is ignored. The frame is notified when the panel is selected.
        """
        if self.left_down:
            self.left_down = False
            gp = self.GetGrandParent()
            if gp != None:
                gp.SelectPanel(self, not self.selected)
        event.Skip()

    def OnDoubleClick(self, event):
        """
        Handle a double-click event.

        Causes the current code to be copied to the clipboard. This also selects the
        panel and causes the frame to be notified.
        """
        self.left_down = False
        gp = self.GetGrandParent()
        if gp != None:
            gp.SelectPanel(self, True)
            # Copy current code to clipboard
            GetLogger().info("%s copying code to the clipboard.", self.GetName())
            if not self.CopyCodeToClipboard():
                wx.Bell()
        event.Skip()

    def OnContextMenu(self, event):
        """Offer choice of provisioning URL or QR code image URL from right-click menu."""
        pos = event.GetPosition()
        cl_pos = self.ScreenToClient(pos)
        self.PopupMenu(self.context_menu, cl_pos)

    def OnProvisioningUri(self, event):
        """Copy the provisioning URI to the clipboard."""
        GetLogger().info("%s copying provisioning URI to the clipboard.", self.GetName())
        if not self.CopyProvisioningUriToClipboard():
            wx.Bell()
        event.Skip()

    def OnQrCodeImage(self, event):
        """Display the QR code image."""
        GetLogger().info("%s displaying QR code image.", self.GetName())
        if not self.DisplayQrCodeImage():
            wx.Bell()
        event.Skip()

    def OnMouseEnter(self, event):
        """Clear mouse button state when the mouse enters the panel."""
        self.left_down = False
        event.Skip()

    def OnMouseLeave(self, event):
        """Clear mouse button state when the mouse leaves the panel."""
        self.left_down = False
        event.Skip()

    def GetEntry(self):
        """Return the authentication store entry associated with the panel."""
        return self.entry

    def SetEntry(self, entry):
        """Set the authentication store entry associated with the panel."""
        self.entry = entry
        self.sort_index = entry.GetSortIndex()
        self.code_digits = entry.GetDigits()
        self.SetName('entry_panel_{0:d}'.format(self.entry.GetGroup()))
        self.code = str(self.entry.GenerateNextCode())
        ## GetLogger().debug( "AEP SE on %s", self.GetName() )
        self.ChangeContents()

    def GetSortIndex(self):
        "Return the panel's sort index."""
        if self.entry != None:
            self.sort_index = self.entry.GetSortIndex()
        return self.sort_index

    def SetSortIndex(self, index):
        """Set the panel's sort index."""
        self.sort_index = index
        if self.entry != None:
            self.entry.SetSortIndex(index)

    def MaskCode(self, state):
        """Set the code masking state of the panel."""
        self.code_masked = state
        self.code_text.SetLabelText(self.GetCodeString(self.selected))

    def ShowTimer(self, state):
        """Set the show-timer state of the panel."""
        self.show_timer = state
        if self.show_timer:
            self.timer_gauge.Show()
        else:
            self.timer_gauge.Hide()
            # AuthFrame knows to check panel sizes and resize after showing/hiding timers

    def GetPanelSize(self):
        """Return the panel's current size."""
        return self.GetSize()

    def GetLabelWidth(self):
        """Return the panel's current label width."""
        w = self.provider_text.GetSize().GetWidth()
        x = self.account_text.GetSize().GetWidth()
        if x > w:
            w = x
        return w

    def SizeLabels(self, label_width):
        """Resize the labels to the given width to keep columns even."""
        ## GetLogger().debug( "AEP SL new label width %d", label_width )
        self.label_width = label_width

        s = self.label_panel.GetClientSize()
        s.SetWidth(self.label_width)
        self.label_panel.SetMinClientSize(s)
        self.label_panel.SetClientSize(s)
        self.Fit()

    def UpdateContents(self):
        """Update the panel's displayed contents based on the current state and entry."""
        if self.entry != None:
            ## GetLogger().debug( "AEP UC updating %s", self.GetName() )
            self.code_text.SetLabelText(self.GetCodeString(self.selected))
            self.provider_text.SetLabelText(self.entry.GetProvider())
            self.provider_text.Fit()
            self.account_text.SetLabelText(self.entry.GetAccount())
            self.account_text.Fit()

        if self.label_width == 0:
            self.label_width = self.GetLabelWidth()

        s = self.label_panel.GetClientSize()
        s.SetWidth(self.label_width)
        self.label_panel.SetMinClientSize(s)
        self.label_panel.SetClientSize(s)
        self.Fit()

        ## GetLogger().debug( "AEP UC provider size: %s", unicode( self.provider_text.GetSize() ) )
        ## GetLogger().debug( "AEP UC account size:  %s", unicode( self.account_text.GetSize() ) )
        ## GetLogger().debug( "AEP UC label width:   %d", self.label_width )
        ## GetLogger().debug( "AEP UC panel size:    %s", unicode( self.GetSize() ) )

    def ChangeContents(self):
        """Handle a change in contents and signal the change to the frame."""
        ## GetLogger().debug( "AEP CC" )
        self.UpdateContents()
        gp = self.GetGrandParent()
        if gp != None:
            ## GetLogger().debug( "AEP CC notifying frame" )
            gp.UpdatePanelSize()

    def Select(self):
        """Select this panel."""
        self.selected = True
        self.SetFocus()
        bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        for item in [self, self.label_panel, self.provider_text, self.account_text,
                     self.code_text, self.timer_gauge]:
            item.SetBackgroundColour(bg)
            item.SetForegroundColour(fg)
        # We always show the code when selected regardless of code_masked
        self.code_text.SetLabelText(self.GetCodeString(True))

    def Deselect(self):
        """Deselect this panel."""
        self.selected = False
        for item in [self, self.label_panel, self.provider_text, self.account_text,
                     self.code_text, self.timer_gauge]:
            item.SetBackgroundColour(wx.NullColour)
            item.SetForegroundColour(wx.NullColour)
        self.code_text.SetLabelText(self.GetCodeString(False))

    def UpdateTimerGauge(self):
        """Update the countdown bar and code based on the current time and cycle."""
        current_time = wx.GetUTCTime()
        ## GetLogger().debug( "AEP %s timer tick %d", self.GetName(), current_time ) # LOTS of debug output
        last_cycle = self.totp_cycle
        self.totp_cycle = current_time % self.totp_period
        # If we wrapped around the end of a cycle, update the code and reset the countdown timer gauge
        if self.totp_cycle < last_cycle and self.entry != None:
            self.code = str(self.entry.GenerateNextCode())
            self.code_text.SetLabelText(self.GetCodeString(self.selected))
        # Make our timer gauge count down to zero
        self.timer_gauge.SetValue(self.totp_period - self.totp_cycle - 1)

    def CopyCodeToClipboard(self):
        """Copy the current code to the clipboard."""
        sts = True
        if wx.TheClipboard.Open():
            if wx.TheClipboard.SetData(wx.TextDataObject(self.code)):
                wx.TheClipboard.Flush()
            else:
                GetLogger().error("%s encountered an error copying the code to the clipboard.", self.GetName())
                sts = False
            wx.TheClipboard.Close()
        else:
            GetLogger().error("%s cannot open clipboard.", self.GetName())
            sts = False
        return sts

    def GetCodeString(self, selected):
        """Generate a string containing the code or mask characters."""
        if self.code_masked and not selected:
            s = self.code_mask_char * self.code_digits
        else:
            s = self.code
        if len(s) < self.code_max_digits:
            pad_len = (self.code_max_digits - len(s)) / 2
            tail_len = self.code_max_digits - len(s) - pad_len
            s = (' ' * pad_len) + s + (' ' * tail_len)
        return s

    def GetProvisioningUri(self):
        return self.entry.GetKeyUri()

    def CopyProvisioningUriToClipboard(self):
        """Copy the provisioning URI to the clipboard."""
        sts = True
        if wx.TheClipboard.Open():
            if wx.TheClipboard.SetData(wx.TextDataObject(self.GetProvisioningUri())):
                wx.TheClipboard.Flush()
            else:
                GetLogger().error("%s encountered an error copying the provisioning URI to the clipboard.",
                                  self.GetName())
                sts = False
            wx.TheClipboard.Close()
        else:
            GetLogger().error("%s cannot open clipboard.", self.GetName())
            sts = False
        return sts

    def DisplayQrCodeImage(self):
        """Display the QR code image."""
        sts = True
        title = self.entry.GetQualifiedAccount()
        fr = QrCodeFrame(self, wx.ID_ANY, title, uri = self.GetProvisioningUri())
        fr.Show()
        return sts
