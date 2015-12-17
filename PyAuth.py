#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import logging
import wx
from wx import xrc as xrc
import Configuration

class PyAuthApp( wx.App ):

    def OnInit( self ):
        # Load XRC resources
        self.xrc_path = sys.path[0] + '/xrc/'
        self.res = xrc.XmlResource( self.xrc_path + 'auth_window.xrc' )
        if self.res == None:
            logging.critical( "Cannot find XML resources file %s", self.xrc_path )
            return False
        
        # Create main frame
        self.frame = self.res.LoadFrame( None, 'main_frame' )
        if self.frame == None:
            logging.critical( "Cannot create main program window" )
            return False
        self.SetTopWindow( self.frame )
        wpos = Configuration.GetLastWindowPosition()
        if wpos != None:
            self.frame.SetPosition( wpos )
        self.frame.Show()
        return True


if __name__ == '__main__':
    logging.basicConfig( level = logging.WARNING )
    
    # Set our configuration file up to be the default configuration source
    cfg = wx.FileConfig( 'PyAuth', "Silverglass Technical", localFilename = 'pyauth.cfg',
                         style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
    cfg.SetRecordDefaults( True )
    wx.Config.Set( cfg )
    # Make sure the directory for our configuration file exists
    cfgfile = wx.FileConfig.GetLocalFileName( 'pyauth.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
    cfgdir = os.path.dirname( cfgfile )
    if not os.path.exists( cfgdir ):
        try:
            os.makedirs( cfgdir )
        except OSError as e:
            logging.critical( "Failed to create config directory %s", cfgdir )
            logging.critical( "Error code %d: %s", e.errno, e.strerror )
            sys.exit()

    loglevel = Configuration.GetLoggingLevel()
    logging.getLogger().setLevel( loglevel )

    logging.info( "Configuration file: %s", cfgfile )

    app = PyAuthApp( False )
    app.MainLoop()

    logging.shutdown()
