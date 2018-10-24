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
from io import BytesIO
import qrcode


class QrCodeImage:
    """Represents a QR code image."""

    def __init__(self, uri, box_size):
        self.uri = uri
        self.box_size = box_size

    def GetImage(self):
        qr = qrcode.QRCode(version = None, box_size = self.box_size)
        qr.add_data(self.uri)
        qr.make(fit = True)
        img = qr.make_image()
        strm = BytesIO()
        img.save(strm, "PNG")
        strm.seek(0)
        image = wx.ImageFromStream(strm, wx.BITMAP_TYPE_PNG)
        return image
