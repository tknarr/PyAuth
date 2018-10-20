# -*- coding: utf-8 -*-

# Copyright (C) 2017 Silverglass Technical
# Author: Todd Knarr (tknarr)

import os
import tempfile
from PIL import Image
import zbarlight

import Errors
import Configuration


class QrCodeUri:
    """Represents a provisioning URI decoded from a QR code image."""

    def __init__(self):
        self.uri = None

    def GetUri(self):
        return self.uri

    def decode_file(self, filename):
        if not os.access(filename, os.F_OK | os.R_OK):
            raise Errors.QrCodeImageFileAccess("Cannot access image file: " + str(filename))
        with open(filename, "rb") as image_file:
            try:
                image = Image.open(image_file)
                image.load()
            except IOError:
                return None
        codes = zbarlight.scan_codes('qrcode', image)
        if len(codes) > 0:
            self.uri = codes[0]
        else:
            self.uri = None
        return self.uri

    def decode_url(self, url):
        # TODO fetch image from url and decode
        pass

    def decode_image(self, image):
        # TODO decode image
        pass
