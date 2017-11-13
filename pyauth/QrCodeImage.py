# -*- coding: utf-8 -*-

# Copyright (C) 2017 Silverglass Technical
# Author: Todd Knarr (tknarr)

import wx
from io import BytesIO

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
