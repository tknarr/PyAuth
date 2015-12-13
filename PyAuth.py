#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
from AuthFrame import AuthFrame
from Configuration import Configuration

class PyAuthApp( wx.App ):

    def OnInit( self ):
        # TODO Create user config directory if it doesn't exist
        # Set our configuration file up to be the default configuration source
        cfg = wx.FileConfig( localFilename = wx.StandardPaths.Get().GetUserConfigDir() + "/" +
                             Configuration.GetAppConfigName() + "/config.cfg",
                             style = wx.CONFIG_USE_LOCAL_FILE )
        cfg.SetRecordDefaults( True )
        wx.Config.Set( cfg )

        # Create main frame
        wpos = Configuration.GetLastWindowPosition()
        self.frame = AuthFrame( None, wx.ID_ANY, "PyAuth", pos = wpos, name = "main_frame" )
        self.SetTopWindow( self.frame )
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
