#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import logging
import argparse
import wx
from AuthFrame import AuthFrame as AuthFrame
from About import about_data
import Configuration

# Command line options:
#   --systray, -s                            Start with the systray icon if possible
#   --minimized, -m                          Start minimized
#   --icons=[white|grey|dark|transparent]    Use icons with the given background, default white

# TODO Implement command-line parsing and options

class PyAuthApp( wx.App ):

    def OnInit( self ):
        initial_systray = None
        initial_minimized = None
        iconset = None
        
        # Set up command-line argument parser
        parser = argparse.ArgumentParser( description="OTP authentication client" )
        parser.add_argument( "-s", "--systray", action = 'store_true', dest = 'systray',
                             help = "Start the program with the notification icon showing" )
        parser.add_argument( "-m", "--minimized", action = 'store_true', dest = 'minimized',
                             help = "Start the program minimized" )
        parser.add_argument( "--icons", metavar = "ICONSET", dest = 'iconset',
                             choices = [ "white", "grey", "dark", "transparent" ],
                             help = "Select a given background for the program icons: %(choices)s" )
        version_string = about_data['name'] + ' ' + about_data['version']
        if 'version-tag' in about_data:
            vt = about_data['version-tag']
            if vt != None and vt != '':
                version_string += ' ' + vt
        parser.add_argument( "--version", action = 'version', version = version_string )
        args = parser.parse_args()
        if args.systray:
            initial_systray = True
        if args.minimized:
            initial_minimized = True
        if args.iconset != None:
            iconset = args.iconset
        
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
                return False

        # Configure logging
        loglevel = Configuration.GetLoggingLevel()
        l = logging.getLogger()
        l.setLevel( loglevel )
        logging.info( "Configuration file: %s", cfgfile )

        # Create and position main frame
        self.frame = AuthFrame( None, wx.ID_ANY, "PyAuth", name = 'main_frame',
                                initial_systray = initial_systray, iconset = iconset )
        if self.frame == None:
            logging.critical( "Cannot create main program window" )
            return False
        self.SetTopWindow( self.frame )
        wpos = Configuration.GetLastWindowPosition()
        if wpos != None:
            self.frame.SetPosition( wpos )

        # Display main frame and start running
        self.frame.Show( self.frame.ShouldShow() )
        return True


    def OnExit( self ):
        logging.info( "Exiting" )
        logging.shutdown()
        return 0

        
if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
