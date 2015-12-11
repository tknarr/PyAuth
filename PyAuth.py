#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import wx
from wx import xrc
import AuthFrame
import Configuration

class PyAuthApp( wx.App ):

    def OnInit( self ):
        # TODO Create user config directory if it doesn't exist
        # Set our configuration file up to be the default configuration source
        cfg = wx.FileConfig( localFilename = wx.StandardPaths.Get().GetUserConfigDir() + "/" +
                             Configuration.GetAppConfigName() + "/config.cfg",
                             style = wx.CONFIG_USE_LOCAL_FILE )
        cfg.SetRecordDefaults( True )
        wx.Config.Set( cfg )
        cfg = None

        # Load XRC resources
        self.xrc_path = sys.path[0] + "/xrc/"
        self.res = xrc.XmlResource( self.xrc_path + "auth_window.xrc" )

        self.frame = self.res.LoadFrame( None, 'main_frame' )
        self.SetTopWindow( self.frame )
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
