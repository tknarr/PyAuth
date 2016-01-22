# -*- coding: utf-8 -*-

import os.path
import logging
import logging.handlers
import Configuration
from About import GetProgramName

def GetLogger():
    return logging.getLogger( GetProgramName() )

def ConfigureLogging( log_filename_args ):
    log_lvl = Configuration.GetLoggingLevel()
    if log_filename_args != None:
        lfn = log_filename_args
    else:
        lfn = Configuration.GetLogFilename()
    if lfn != None and lfn != '':
        log_filename = os.path.expandvars( os.path.expanduser( lfn ) )
        max_size = Configuration.GetLogMaxSize()
        backup_count = Configuration.GetLogBackupCount()
    else:
        log_filename = None

    app_logger = logging.getLogger( GetProgramName() )

    # Console logger with just serious errors
    formatter = logging.Formatter( '%(levelname)s:%(name)s:%(message)s' )
    handler = logging.StreamHandler()
    handler.setFormatter( formatter )
    handler.setLevel( logging.ERROR )
    app_logger.addHandler( handler )
    
    # File logger with all messages
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
