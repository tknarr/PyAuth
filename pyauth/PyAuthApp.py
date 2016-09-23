# -*- coding: utf-8 -*-
"""Application main module."""

## PyAuth - Google Authenticator desktop application
## Copyright (C) 2016 Todd T Knarr <tknarr@silverglass.org>

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see http://www.gnu.org/licenses/

import sys
import os.path
import logging
import argparse
import pkg_resources
import wx
import Configuration
from AuthFrame import AuthFrame as AuthFrame
from About import GetProgramVersionString, GetProgramName, GetVendorName
from Logging import ConfigureLogging, GetLogger


class PyAuthApp( wx.App ):
    """Application main class."""

    def OnInit( self ):
        """Initialize the application."""

        initial_systray = None
        initial_minimized = None
        iconset = None
        log_filename = None
        log_level = None

        # Default root logging for startup messages
        logging.basicConfig( level = logging.WARNING )

        # Set up command-line argument parser
        program_name = GetProgramName( )
        parser = argparse.ArgumentParser( description = "OTP authentication client" )
        parser.add_argument( "-s", "--systray", action = 'store_true', dest = 'systray',
                             help = "Start the program with the notification icon showing" )
        parser.add_argument( "-m", "--minimized", action = 'store_true', dest = 'minimized',
                             help = "Start the program minimized to the notification icon (implies -s)" )
        parser.add_argument( "-n", "--no-systray", action = "store_true", dest = 'normal',
                             help = "Start as a normal window, overrides -s and -m" )
        parser.add_argument( "--icons", metavar = "ICONSET", dest = 'iconset',
                             choices = [ "white", "grey", "dark", "transparent" ],
                             help = "Select a given background for the program icons: %(choices)s" )
        parser.add_argument( "--logfile", metavar = "FILENAME", dest = 'logfile', default = None,
                             help = "Redirect logging to the named file, may include user and variable expansion" )
        parser.add_argument( "--no-logfile", action = 'store_true', dest = 'no_logfile',
                             help = "Suppress the log file completely" )
        parser.add_argument( "--loglevel", metavar = "LEVEL", dest = 'loglevel', default = '',
                             choices = [ 'critical', 'error', 'warning', 'info', 'debug' ],
                             help = "Set the logging level: %(choices)s" )
        parser.add_argument( "--version", action = 'version',
                             version = GetProgramName( ) + ' ' + GetProgramVersionString( ) )
        args = parser.parse_args( )
        if args.systray:
            initial_systray = True
        if args.minimized:
            initial_minimized = True
            initial_systray = True
        if args.normal:
            initial_minimized = False
            initial_systray = False
        if args.iconset != None:
            iconset = args.iconset
        if args.no_logfile:
            log_filename = ''
        else:
            if args.logfile != None:
                log_filename = args.logfile
        if args.loglevel != None:
            log_level = args.loglevel

        self.SetAppName( program_name )

        # Set our configuration file up to be the default configuration source
        cfg = wx.FileConfig( GetProgramName( ), GetVendorName( ), localFilename = 'pyauth.cfg',
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
        if self.instance_check.IsAnotherRunning( ):
            logging.critical( "A copy of " + GetProgramName( ) + " is already running." )
            return False

        # Configure logging
        ConfigureLogging( log_filename, log_level )
        GetLogger( ).info( "Configuration file: %s", cfgfile )

        # Create and position main frame
        wpos = Configuration.GetLastWindowPosition( )
        wsize = Configuration.GetLastWindowSize( )
        self.frame = AuthFrame( None, wx.ID_ANY, "PyAuth", name = 'main_frame',
                                pos = wpos, size = wsize,
                                initial_systray = initial_systray,
                                initial_minimized = initial_minimized,
                                iconset = iconset )
        if self.frame == None:
            logging.critical( "Cannot create main program window" )
            return False
        self.SetTopWindow( self.frame )

        # Display main frame and start running
        # If we're starting minimized and are in the systray, leave the frame
        # hidden. If we're starting minimized and aren't in the systray, minimize
        # the frame as soon as it's shown. If we aren't starting minimized, show
        # the frame.
        self.frame.Show( not self.frame.StartMinimized( ) )
        return True

    def OnExit( self ):
        """Handle the exit event."""
        GetLogger( ).info( "Exiting" )
        logging.shutdown( )
        return 0
