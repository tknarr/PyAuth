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
import qrcode
from io import BytesIO


class QrCodeImage:
    """Represents a QR code image."""

    def __init__( self, entry ):
        self.provisioning_uri = entry.GetKeyUri( )

    def GetImage( self ):
        img = qrcode.make( self.provisioning_uri )
        strm = BytesIO( )
        img.save( strm, "PNG" )
        strm.seek( 0 )
        image = wx.ImageFromStream( strm, wx.BITMAP_TYPE_PNG )
        return image


class QrCodeFrame( wx.Frame ):
    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr, image = None, border = 0 ):
        self.border = border
        self.x_loc = border
        self.y_loc = border
        self.bitmap = image.ConvertToBitmap( )

        wx.Frame.__init__( self, parent, id, title, pos, size, style, name )

        client_size = self.bitmap.GetSize( )
        client_size.IncBy( self.border * 2, self.border * 2 )
        self.SetClientSize( client_size )

        self.Bind( wx.EVT_PAINT, self.OnPaint )

    def OnPaint( self, event ):
        dc = wx.PaintDC( self )
        dc.DrawBitmap( self.bitmap, self.x_loc, self.y_loc )
