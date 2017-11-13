# -*- coding: utf-8 -*-

# Copyright (C) 2017 Silverglass Technical
# Author: Todd Knarr (tknarr)

import qrtools
import tempfile

import Configuration


class QrCodeUri:
    """Represents a provisioning URI decoded from a QR code image."""

    def __init__(self):
        self.uri = None
        self.temp_dir = Configuration.GetConfigDirectory()
        self.qr = qrtools.QR()

    def GetUri(self):
        return self.uri

    def decode_file(self, filename):
        # TODO decode file
        pass

    def decode_url(self, url):
        # TODO fetch image from url and decode
        pass

    def decode_image(self, image):
        temp_file = tempfile.NamedTemporaryFile(dir = self.temp_dir, suffix = ".png")
        # TODO write image into temp file
        self.uri = self.decode_file(temp_file.name)
        temp_file.close()
        return self.uri
