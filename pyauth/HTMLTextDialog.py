# -*- coding: utf-8 -*-
"""HTML text display dialog box."""

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
import wx.html

from Logging import GetLogger


class ClickableHTMLWindow(wx.html.HtmlWindow):
    """Clickable HTML window."""

    def __init__(self, parent, id = wx.ID_ANY, size = wx.DefaultSize):
        """Initialize the window."""
        wx.html.HtmlWindow.__init__(self, parent, id, size = size)
        if 'gtk2' in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        """Handle clicking on a link by launching a browser."""
        wx.LaunchDefaultBrowser(link.GetHref())


class HTMLTextDialog(wx.Dialog):
    """Display HTML text in a dialog box."""

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME | wx.RESIZE_BORDER,
                 name = wx.DialogNameStr):
        """Initialize the dialog box."""
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)

        GetLogger().debug("HTML text dialog init")

        self.browser = None

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        vbox.AddSpacer(16, 0)

        html = ClickableHTMLWindow(self, wx.ID_ANY, size = wx.Size(600, 600))
        self.browser = html
        vbox.Add(html, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)

        vbox.AddSpacer(16, 0)

        btnsizer = self.CreateButtonSizer(wx.OK)
        if btnsizer != None:
            vbox.Add(btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)

        self.GetSizer().Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK)

        GetLogger().debug("HTML text dialog init done")

    def SetPage(self, src):
        """Set the HTML source code to display."""
        if self.browser != None:
            self.browser.SetPage(src)

    def OnOK(self, event):
        """Handle the OK button to dismiss the dialog box."""
        event.Skip(True)
