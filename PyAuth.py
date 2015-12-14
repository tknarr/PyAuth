#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
from AuthFrame import AuthFrame
import Configuration

class PyAuthApp( wx.App ):

    def OnInit( self ):
        # Set our configuration file up to be the default configuration source
        cfg = wx.FileConfig( "PyAuth", "Silverglass Technical", localFilename = "pyauth.cfg",
                             style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        cfg.SetRecordDefaults( True )
        wx.Config.Set( cfg )
        # TODO Make sure our config directory exists

        # Create main frame
        wpos = Configuration.GetLastWindowPosition()
        self.frame = AuthFrame( None, wx.ID_ANY, "PyAuth", pos = wpos, name = "main_frame" )
        self.SetTopWindow( self.frame )
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
