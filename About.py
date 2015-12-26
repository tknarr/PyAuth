# -*- coding: utf-8 -*-

import wx
from wx.lib.wordwrap import wordwrap

about_data = {
    'name': "PyAuth",
    'version': '0.1.1',
    'version-tag': 'dev',
    'copyright': "(C) 2015 Todd T Knarr",
    'website': 'https://github.com/tknarr/PyAuth.git',
    'developers': [ 'Todd T Knarr' ],
    'description': "Google Authenticator desktop application",

    'license': """\
PyAuth - Google Authenticator desktop application
Copyright (C) 2015 Todd T Knarr

This program is free software: you can redistribute it and/or modify \
it under the terms of the GNU General Public License as published by \
the Free Software Foundation, either version 3 of the License, or \
(at your option) any later version.

This program is distributed in the hope that it will be useful, \
but WITHOUT ANY WARRANTY; without even the implied warranty of \
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \
GNU General Public License for more details.

You should have received a copy of the GNU General Public License \
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

    }

def GetAboutInfo( dc, desc_width = 350 ):
    about_info = wx.AboutDialogInfo()
    about_info.SetName( about_data['name'] )
    version_string = about_data['version']
    if 'version-tag' in about_data:
        vt = about_data['version-tag']
        if vt != None and vt != '':
            version_string += ' ' + vt
    about_info.SetVersion( version_string )
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
