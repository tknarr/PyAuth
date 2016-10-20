# -*- coding: utf-8 -*-
"""Database password dialog box."""

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


class DatabasePasswordDialog(wx.Dialog):
    """Database password dialog box."""

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.DEFAULT_DIALOG_STYLE, name = wx.DialogNameStr):
        """Initialize the dialog box."""
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)

        GetLogger().debug("PWD init")

        self.password_label = None
        self.password_text = None

        self.password_literal = "Enter your password:"

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        vbox.AddSpacer(16, 0)

        # Password
        lbl = wx.StaticText(self, wx.ID_ANY, '')
        self.MakeLabel(lbl, self.password_literal)
        vbox.Add(lbl, 0, wx.LEFT | wx.RIGHT, 8)
        self.password_label = lbl
        txt = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP | wx.TE_PASSWORD)
        te = txt.GetTextExtent('M' * 20)
        txt.SetMinClientSize(wx.DLG_SZE(self, te))
        vbox.Add(txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)
        self.password_text = txt

        vbox.AddSpacer(16, 0)

        vbox.AddStretchSpacer(1)

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if btnsizer != None:
            vbox.Add(btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)

        self.GetSizer().Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK)

        GetLogger().debug("PWD init done")

    def SetFocus(self):
        self.password_text.SetFocus()

    def OnOK(self, event):
        """Handle the OK button event."""
        GetLogger().debug("PWD OK button")
        event.Skip(True)

    def GetPasswordValue(self):
        """Return the contents of the password field."""
        return self.password_text.GetValue()

    def Reset(self):
        """Reset the dialog box contents."""
        GetLogger().debug("PWD reset")
        self.password_text.Clear()
        self.SetFocus()

    def MakeLabel(self, ctrl, txt):
        """Set up a label control's text."""
        ctrl.SetLabelText(txt)
        ctrl.SetMinSize(wx.DLG_SZE(self, ctrl.GetTextExtent(ctrl.GetLabelText())))
