# -*- coding: utf-8 -*-
"""Metadata about the program."""

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

import pkg_resources
import pyauth
from Logging import GetLogger

about_data = {
    'name':           pyauth.__program_name__,
    'version':        pyauth.__version__,
    'version-tag':    pyauth.__version_tag__,
    'version-status': pyauth.__version_status__,
    'copyright':      "(C) 2016 Todd T Knarr\nLicense: GPL v3.0 or any later version",
    'website':        'https://github.com/tknarr/PyAuth.git',
    'developers':     ['Todd T Knarr'],
    'description':    "Google Authenticator desktop application",
}


def GetProgramName():
    """Program's canonical name."""
    return about_data['name']


def GetProgramVersion():
    """Standard version number."""
    return about_data['version'] + about_data['version-tag']


def GetProgramVersionString():
    """Extended version number."""
    v = GetProgramVersion()
    if about_data['version-status'] != '':
        v += ' (' + about_data['version-status'] + ')'
    return v


def GetVendorName():
    """Software vendor's name."""
    return "Silverglass Technical"


def GetAboutInfo(dc, desc_width = 600):
    """Fill in and return the About dialog box info structure."""

    about_info = wx.AboutDialogInfo()
    about_info.SetName(about_data['name'])
    about_info.SetVersion(GetProgramVersionString())
    about_info.SetCopyright(about_data['copyright'])
    about_info.SetWebSite(about_data['website'])
    about_info.SetDescription(about_data['description'])
    for s in about_data['developers']:
        about_info.AddDeveloper(s)
    if 'docwriters' in about_data:
        for x in about_data['docwriters']:
            about_info.AddDocWriter(s)
    if 'translators' in about_data:
        for x in about_data['translators']:
            about_info.AddTranslator(s)
    return about_info


def GetIconBundle(name):
    """
    Find and return the program's icon bundle.

    The name indicates the color/kind of background desired for the icons.
    """

    icon_bundle = None
    filename = 'images/' + GetProgramName()
    if name != 'transparent':
        filename += '-' + name
    filename += '.ico'
    try:
        input_strm = pkg_resources.resource_stream('pyauth', filename)
        icon_bundle = wx.IconBundleFromStream(input_strm, wx.BITMAP_TYPE_ICO)
    except Exception as e:
        GetLogger().error("Error in %s icon bundle: %s", name, unicode(e))
    return icon_bundle


def GetTaskbarIcon(name):
    """
    Find and return the program's notification bar icon.

    The name indicates the color/kind of background desired for the icon.
    """

    icon = None
    filename = 'images/' + GetProgramName() + '-systray'
    if name != 'transparent':
        filename += '-' + name
    filename += '.png'
    try:
        input_strm = pkg_resources.resource_stream('pyauth', filename)
        img = wx.ImageFromStream(input_strm, wx.BITMAP_TYPE_PNG)
        bm = img.ConvertToBitmap()
        if bm != None:
            icon = wx.IconFromBitmap(bm)
    except Exception as e:
        GetLogger().error("Error in %s taskbar icon: %s", name, unicode(e))
    return icon
