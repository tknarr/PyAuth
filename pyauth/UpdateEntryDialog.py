# -*- coding: utf-8 -*-
"""Update entry dialog box."""

#-----
# PyAuth
# Copyright (C) 2018 Silverglass Technical
# Author: Todd Knarr <tknarr@silverglass.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-----

import wx

from Logging import GetLogger


class UpdateEntryDialog(wx.Dialog):
    """Update entry dialog box."""

    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.DEFAULT_DIALOG_STYLE, name = wx.DialogNameStr):
        """Initialize the dialog box."""
        wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)

        GetLogger().debug("UED init")

        self.provider_label = None
        self.provider_text = None
        self.account_label = None
        self.account_text = None
        self.secret_label = None
        self.secret_text = None
        self.digits_label = None
        self.digits_radio = None

        self.provider_literal = "Provider:"
        self.account_literal = "Account:"
        self.secret_literal = "Secret:"
        self.digits_literal = "Digits in code:"
        self.required_literal = "(required)"

        self.text_color = self.GetForegroundColour()

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        vbox.AddSpacer(16, 0)

        # Provider
        lbl = wx.StaticText(self, wx.ID_ANY, '')
        self.MakeLabel(lbl, self.provider_literal, True)
        vbox.Add(lbl, 0, wx.LEFT | wx.RIGHT, 8)
        self.provider_label = lbl
        txt = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP)
        te = txt.GetTextExtent('MMMMMMMMMMMMMMMMMMMM')
        txt.SetMinClientSize(wx.DLG_SZE(self, te))
        vbox.Add(txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)
        self.provider_text = txt

        vbox.AddSpacer(16, 0)

        # Account
        lbl = wx.StaticText(self, wx.ID_ANY, '')
        self.MakeLabel(lbl, self.account_literal, True)
        vbox.Add(lbl, 0, wx.LEFT | wx.RIGHT, 8)
        self.account_label = lbl
        txt = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP)
        te = txt.GetTextExtent('MMMMMMMMMMMMMMMMMMMM')
        txt.SetMinClientSize(wx.DLG_SZE(self, te))
        vbox.Add(txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)
        self.account_text = txt

        vbox.AddSpacer(16, 0)

        # Secret
        lbl = wx.StaticText(self, wx.ID_ANY, '')
        self.MakeLabel(lbl, self.secret_literal, True)
        vbox.Add(lbl, 0, wx.LEFT | wx.RIGHT, 8)
        self.secret_label = lbl
        txt = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP)
        te = txt.GetTextExtent('MMMMMMMMMMMMMMMMMMMM')
        txt.SetMinClientSize(wx.DLG_SZE(self, te))
        vbox.Add(txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8)
        self.secret_text = txt

        vbox.AddSpacer(16, 0)

        # Digits in code
        lbl = wx.StaticText(self, wx.ID_ANY, '')
        self.MakeLabel(lbl, self.digits_literal, False)
        vbox.Add(lbl, 0, wx.LEFT | wx.RIGHT, 8)
        self.digits_label = lbl
        rbox = wx.RadioBox(self, wx.ID_ANY, choices = ["6", "8"])
        vbox.Add(rbox, 0, wx.LEFT | wx.RIGHT, 8)
        self.digits_radio = rbox

        vbox.AddSpacer(16, 0)

        vbox.AddStretchSpacer(1)

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if btnsizer != None:
            vbox.Add(btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)

        self.GetSizer().Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK)

        GetLogger().debug("UED init done")

    def SetFocus(self):
        self.provider_text.SetFocus()

    def OnOK(self, event):
        """Handle the OK button and check for required fields."""
        err = False
        f = self.provider_text.IsEmpty()
        err = err or f
        self.ColorLabel(self.provider_label, f)
        f = self.account_text.IsEmpty()
        err = err or f
        self.ColorLabel(self.account_label, f)
        f = self.secret_text.IsEmpty()
        err = err or f
        self.ColorLabel(self.secret_label, f)
        if err:
            GetLogger().debug("UED OK button missing required items")
            wx.Bell()
        else:
            GetLogger().debug("UED OK button")
            event.Skip(True)

    def GetProviderValue(self):
        """Return the contents of the provider field."""
        return self.provider_text.GetValue()

    def GetAccountValue(self):
        """Return the contents of the account field."""
        return self.account_text.GetValue()

    def GetSecretValue(self):
        """Return the contents of the secret field."""
        return self.secret_text.GetValue()

    def GetDigitsValue(self):
        """Return the value of the digits selection."""
        return 6 + (self.digits_radio.GetSelection() * 2)

    def Reset(self, provider, account, secret, digits):
        """Reset the contents of the dialog box to the initial state."""
        GetLogger().debug("UED reset")
        self.provider_text.SetValue(provider)
        self.ColorLabel(self.provider_label, self.provider_text.IsEmpty())
        self.account_text.SetValue(account)
        self.ColorLabel(self.account_label, self.account_text.IsEmpty())
        self.secret_text.SetValue(secret)
        self.ColorLabel(self.secret_label, self.secret_text.IsEmpty())
        self.digits_radio.SetSelection((digits - 6) / 2)
        self.SetFocus()

    def ColorLabel(self, ctrl, error):
        """Set the color of the label depending on the error state."""
        if error:
            ctrl.SetForegroundColour(wx.RED)
        else:
            ctrl.SetForegroundColour(self.text_color)

    def MakeLabel(self, ctrl, txt, required):
        """Set up the text of a label control."""
        lbl = txt
        if required:
            lbl += ' ' + self.required_literal
        ctrl.SetLabelText(lbl)
        ctrl.SetMinSize(wx.DLG_SZE(self, ctrl.GetTextExtent(ctrl.GetLabelText())))
