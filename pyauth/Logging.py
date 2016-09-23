# -*- coding: utf-8 -*-
"""Logging setup."""

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

import os.path
import logging
import logging.handlers
# NOTE: We need to get the program name directly from the package, because
# the About module whose GetProgramName() function we'd normally use needs
# to use Logger and that sets up an import loop.
import pyauth
import Configuration


def GetLogger( ):
    """Return the standard logger for the program."""
    return logging.getLogger( pyauth.__program_name__ )


def ConfigureLogging( log_filename_args, log_level_args ):
    """
    Set up logging for the rest of the program.

    The two arguments indicate the filename and log level the user requested
    via command-line arguments, overriding what's stored in the program's
    configuration file.
    """

    # If we were given a log-level argument, try to use it. If we weren't given
    # one or it isn't valid, use what's in the configuration file.
    if log_level_args == None or log_level_args == '':
        log_lvl = Configuration.GetLoggingLevel( )
    else:
        log_lvl = getattr( logging, log_level_args.upper( ), None )
        if not isinstance( log_lvl, int ):
            log_lvl = Configuration.GetLoggingLevel( )

    if log_filename_args == None:
        lfn = Configuration.GetLogFilename( )
    else:
        lfn = log_filename_args
    if lfn == None or lfn == '':
        log_filename = None
    else:
        log_filename = os.path.expandvars( os.path.expanduser( lfn ) )
        max_size = Configuration.GetLogMaxSize( )
        backup_count = Configuration.GetLogBackupCount( )

    app_logger = logging.getLogger( pyauth.__program_name__ )

    # Console logger with just serious errors, unless no log file in which case the console
    # becomes the log file and gets all messages requested
    formatter = logging.Formatter( '%(levelname)s:%(name)s:%(message)s' )
    handler = logging.StreamHandler( )
    handler.setFormatter( formatter )
    if log_filename == None:
        handler.setLevel( log_lvl )
    else:
        handler.setLevel( logging.ERROR )
    app_logger.addHandler( handler )

    # File logger with all messages requested
    if log_filename != None:
        # Tab-separated fields
        formatter = logging.Formatter( '%(asctime)s %(levelname)s: %(message)s' )
        # Rotate file based on size
        handler = logging.handlers.RotatingFileHandler( log_filename, maxBytes = max_size,
                                                        backupCount = backup_count, delay = True )
        handler.setFormatter( formatter )
        handler.setLevel( log_lvl )
        app_logger.addHandler( handler )

    app_logger.setLevel( log_lvl )
    # We'll get duplicate and excessive messages if we propagate to the
    # root logger.
    app_logger.propagate = False
