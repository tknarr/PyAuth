# -*- coding: utf-8 -*-

import wx
from wx.lib.wordwrap import wordwrap

about_info = {
    'name': "PyAuth",
    'version': '0.1.1',
    'version-tag': 'dev',
    'copyright': "(C) 2015 Todd Knarr",
    'website': 'https://github.com/tknarr/PyAuth.git',
    'developers': [ 'Todd Knarr' ],
    'license': "GPL v3 or any later version",
    'description': "Google Authenticator desktop application"
    }

def GetAboutInfo( dc, desc_width = 350 ):
    info = wx.AboutDialogInfo()

    info.SetName( about_info['name'] )
    version_string = about_info['version']
    if 'version-tag' in about_info:
        vt = about_info['version-tag']
        if vt != None and vt != '':
            version_string += ' ' + vt
    info.SetVersion( version_string )
    info.SetCopyright( about_info['copyright'] )
    info.SetWebSite( about_info['website'] )
    info.SetLicense( wordwrap( about_info['license'], desc_width, dc ) )
    info.SetDescription( about_info['description'] )
    for s in about_info['developers']:
        info.AddDeveloper( s )
    if 'docwriters' in about_info:
        for x in about_info['docwriters']:
            info.AddDocWriter( s )
    if 'translators' in about_info:
        for x in about_info['translators']:
            info.AddTranslator( s )

    return info
