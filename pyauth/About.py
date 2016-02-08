# -*- coding: utf-8 -*-

import sysconfig
import base64
import io
import wx
from wx.lib.wordwrap import wordwrap
import pyauth
from .Logging import GetLogger

about_data = {
    'name': pyauth.__program_name__,
    'version': pyauth.__version__,
    'version-tag': pyauth.__version_tag__,
    'copyright': "(C) 2016 Todd T Knarr",
    'website': 'https://github.com/tknarr/PyAuth.git',
    'developers': [ 'Todd T Knarr' ],
    'description': "Google Authenticator desktop application",

    'license': """\
PyAuth - Google Authenticator desktop application
Copyright (C) 2016 Todd T Knarr <tknarr@silverglass.org>

This program is free software: you can redistribute it and/or modify \
it under the terms of the GNU General Public License as published by \
the Free Software Foundation, either version 3 of the License, or \
(at your option) any later version.

This program is distributed in the hope that it will be useful, \
but WITHOUT ANY WARRANTY; without even the implied warranty of \
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \
GNU General Public License for more details.

You should have received a copy of the GNU General Public License \
along with this program.  If not, see http://www.gnu.org/licenses/
"""

    }

def GetProgramName():
    return about_data['name']

def GetProgramVersion():
    return about_data['version'] + about_data['version-tag']

def GetProgramVersionString():
    return about_data['name'] + ' ' + GetProgramVersion()

def GetVendorName():
    return "Silverglass Technical"

def GetAboutInfo( dc, desc_width = 600 ):
    about_info = wx.AboutDialogInfo()
    about_info.SetName( about_data['name'] )
    about_info.SetVersion( GetProgramVersion() )
    about_info.SetCopyright( about_data['copyright'] )
    about_info.SetWebSite( about_data['website'] )
    about_info.SetLicense( wordwrap( about_data['license'], desc_width, dc ) )
    about_info.SetDescription( about_data['description'] )
    for s in about_data['developers']:
        about_info.AddDeveloper( s )
    if 'docwriters' in about_data:
        for x in about_data['docwriters']:
            about_info.AddDocWriter( s )
    if 'translators' in about_data:
        for x in about_data['translators']:
            about_info.AddTranslator( s )
    return about_info

def GetIconBundle( name ):
    icon_bundle = None
    scheme = wx.GetApp().install_scheme
    if scheme != None:
        filename = sysconfig.get_path( 'data', scheme ) + '/share/' + GetProgramName()
    else:
        filename = sysconfig.get_path( 'data' ) + '/share/' + GetProgramName()
    filename += '/' + GetProgramName()
    if name != 'transparent':
        filename += '-' + name
    filename += '.ico'
    try:
        input_strm = wx.InputStream( io.FileIO( filename ) )
        icon_bundle = wx.IconBundleFromStream( input_strm, wx.BITMAP_TYPE_ICO )
    except Exception as e:
        GetLogger().error( "Error in %s icon bundle: %s", name, str( e ) )
    return icon_bundle

def GetTaskbarIcon( name ):
    icon = None
    scheme = wx.GetApp().install_scheme
    if scheme != None:
        filename = sysconfig.get_path( 'data', scheme ) + \
            '/share/icons/hicolor/32x32/apps/' + GetProgramName() + '-systray'
    else:
        filename = sysconfig.get_path( 'data' ) + \
            '/share/icons/hicolor/32x32/apps/' + GetProgramName() + '-systray'
    if name != 'transparent':
        filename += '-' + name
    filename += '.png'
    try:
        input_strm = wx.InputStream( io.FileIO( filename ) )
        img = wx.ImageFromStream( input_strm, wx.BITMAP_TYPE_PNG )
        bm = img.ConvertToBitmap()
        if bm != None:
            icon = wx.IconFromBitmap( bm )
    except Exception as e:
        GetLogger().error( "Error in %s taskbar icon: %s", name, str(e) )
    return icon
