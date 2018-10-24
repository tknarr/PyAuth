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
