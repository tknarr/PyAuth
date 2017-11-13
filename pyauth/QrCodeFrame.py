# -*- coding: utf-8 -*-

# Copyright (C) 2017 Silverglass Technical
# Author: Todd Knarr (tknarr)

import wx

from QrCodePanel import QrCodePanel


class QrCodeFrame(wx.Frame):
    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr, uri = None, border = 0):
        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)
        self.panel = QrCodePanel(self, uri = uri, border = border)
        self.panel.SetFocus()
