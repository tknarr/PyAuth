# -*- coding: utf-8 -*-

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

from QrCodePanel import QrCodePanel


class QrCodeFrame(wx.Frame):
    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr, uri = None, border = 0):
        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)
        self.panel = QrCodePanel(self, uri = uri, border = border)
        self.panel.SetFocus()
