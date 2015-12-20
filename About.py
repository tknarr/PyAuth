# -*- coding: utf-8 -*-

import wx
from wx.lib.wordwrap import wordwrap

about_data = {
    'name': "PyAuth",
    'version': '0.1.1',
    'version-tag': 'dev',
    'copyright': "(C) 2015 Todd Knarr",
    'website': 'https://github.com/tknarr/PyAuth.git',
    'developers': [ 'Todd Knarr' ],
    'license': "GPL v3 or any later version",
    'description': "Google Authenticator desktop application"
    }
about_info = None

def GetAboutInfo( dc, desc_width = 350 ):
    if about_info == None:
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
