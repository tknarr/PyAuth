# -*- coding: utf-8 -*-
"""Generate a QR code image for an entry."""

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
from io import BytesIO

import Configuration
import qrcode


class QrCodeImage:
    """Represents a QR code image."""

    def __init__(self, uri, box_size):
        self.uri = uri
        self.box_size = box_size

    def GetImage(self):
        qr = qrcode.QRCode(version = None, box_size = self.box_size,
                           error_correction = qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(self.uri)
        qr.make(fit = True)
        img = qr.make_image()
        strm = BytesIO()
        img.save(strm, "PNG")
        strm.seek(0)
        image = wx.ImageFromStream(strm, wx.BITMAP_TYPE_PNG)
        return image


class QrCodePanel(wx.Panel):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr, uri = None, border = 0):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)

        self.box_size = Configuration.GetQRBoxSize()
        self.uri = uri
        self.border = border
        self.x_loc = border
        self.y_loc = border

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.UpdateImage()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, self.x_loc, self.y_loc)

    def OnShow(self, event):
        event.Skip()

    def UpdateImage(self):
        image = QrCodeImage(self.uri, self.box_size).GetImage()
        self.bitmap = image.ConvertToBitmap()
        client_size = self.bitmap.GetSize()
        client_size.IncBy(self.border * 2, self.border * 2)
        self.SetClientSize(client_size)
        self.SetMinClientSize(client_size)
        win_size = self.ClientToWindowSize(client_size)
        p = self.GetParent()
        frame_size = p.ClientToWindowSize(win_size)
        p.SetSizeHints(-1, -1)
        p.SetClientSize(win_size)
        p.SetMinClientSize(win_size)
        p.SetSizeHints(frame_size.GetWidth(), frame_size.GetHeight(),
                       maxW = frame_size.GetWidth(), maxH = frame_size.GetHeight())
        p.Refresh()


class QrCodeFrame(wx.Frame):
    def __init__(self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize, \
                 style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr, uri = None, border = 0):
        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)
        self.panel = QrCodePanel(self, uri = uri, border = border)
        self.panel.SetFocus()
