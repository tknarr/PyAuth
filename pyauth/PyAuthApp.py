# -*- coding: utf-8 -*-

import sys
import os.path
import logging
import argparse
import wx
from . import Configuration
from .AuthFrame import AuthFrame as AuthFrame
from .About import GetProgramVersionString, GetProgramName, GetVendorName
from .Logging import ConfigureLogging, GetLogger

# Command line options:
#   --systray, -s                            Start with the systray icon if possible
#   --minimized, -m                          Start minimized to the systray (implies -s)
#   --icons=(white|grey|dark|transparent)    Use icons with the given background, default white
#   --logfile=<filename>                     Redirect log to named file

class PyAuthApp( wx.App ):

    def OnInit( self ):
        initial_systray = None
        initial_minimized = None
        iconset = None
        log_filename = None

        # Default root logging for startup messages
        logging.basicConfig( level = logging.WARNING )

        # Set up command-line argument parser
        program_name = GetProgramName()
        parser = argparse.ArgumentParser( description="OTP authentication client" )
        parser.add_argument( "-s", "--systray", action = 'store_true', dest = 'systray',
                             help = "Start the program with the notification icon showing" )
        parser.add_argument( "-m", "--minimized", action = 'store_true', dest = 'minimized',
                             help = "Start the program minimized to the notification icon (implies -s)" )
        parser.add_argument( "--icons", metavar = "ICONSET", dest = 'iconset',
                             choices = [ "white", "grey", "dark", "transparent" ],
                             help = "Select a given background for the program icons: %(choices)s" )
        parser.add_argument( "--logfile", metavar = "FILENAME", dest = 'logfile', default = None,
                             help = "Redirect logging to the named file, may include user and variable expansion" )
        parser.add_argument( "--version", action = 'version', version = GetProgramVersionString() )
        args = parser.parse_args()
        if args.systray:
            initial_systray = True
        if args.minimized:
            initial_minimized = True
            initial_systray = True
        if args.iconset != None:
            iconset = args.iconset
        if args.logfile != None:
            log_filename = args.logfile
        
        self.SetAppName( program_name )

        # Set our configuration file up to be the default configuration source
        cfg = wx.FileConfig( GetProgramName(), GetVendorName(), localFilename = 'pyauth.cfg',
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

        # Only allow one instance pointed at a given config/database directory to run
        self.instance_check = wx.SingleInstanceChecker( '.lock', cfgdir )
        if self.instance_check.IsAnotherRunning():
            logging.critical( "A copy of " + GetProgramName() + " is already running." )
            return False

        # Configure logging
        ConfigureLogging( log_filename )
        GetLogger().info( "Configuration file: %s", cfgfile )

        # Create and position main frame
        self.frame = AuthFrame( None, wx.ID_ANY, "PyAuth", name = 'main_frame',
                                initial_systray = initial_systray,
                                initial_minimized = initial_minimized,
                                iconset = iconset )
        if self.frame == None:
            logging.critical( "Cannot create main program window" )
            return False
        self.SetTopWindow( self.frame )
        wpos = Configuration.GetLastWindowPosition()
        if wpos != None:
            self.frame.SetPosition( wpos )

        self.Bind( wx.EVT_QUERY_END_SESSION, self.OnQES )
        self.Bind( wx.EVT_END_SESSION, self.OnES )

        # Display main frame and start running
        # If we're starting minimized and are in the systray, leave the frame
        # hidden. If we're starting minimized and aren't in the systray, minimize
        # the frame as soon as it's shown. If we aren't starting minimized, show
        # the frame.
        self.frame.Show( not ( initial_minimized and self.frame.InSystray() ) )
        return True


    def OnQES( self, event ):
        GetLogger().info( "Event: query end session" )
        event.Skip()

    def OnES( self, event ):
        GetLogger().info( "Event: end session" )
        event.Skip()


    def OnExit( self ):
        GetLogger().info( "Exiting" )
        logging.shutdown()
        return 0
