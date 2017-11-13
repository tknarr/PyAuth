# -*- coding: utf-8 -*-

# Copyright (C) 2017 Silverglass Technical
# Author: Todd Knarr (tknarr)

import os
import tempfile
import qrcode

import Errors
import Configuration


class QrCodeUri:
    """Represents a provisioning URI decoded from a QR code image."""

    def __init__(self):
        self.uri = None
        self.temp_dir = Configuration.GetConfigDirectory()

    def GetUri(self):
        return self.uri

    def decode_file(self, filename):
        if not os.access(filename, os.F_OK | os.R_OK):
            raise Errors.QrCodeImageFileAccess("Cannot access image file: " + str(filename))
        if self.qr.decode(filename):
            self.uri = self.qr.data_to_string()
        else:
            self.uri = None
        return self.uri

    def decode_url(self, url):
        # TODO fetch image from url and decode
        pass

    def decode_image(self, image):
        temp_file = tempfile.NamedTemporaryFile(dir = self.temp_dir, suffix = ".png")
        # TODO write image into temp file
        self.uri = self.decode_file(temp_file.name)
        temp_file.close()
        return self.uri
