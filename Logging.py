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
    if lfn != None:
        log_filename = os.path.expandvars( os.path.expanduser( lfn ) )
        max_size = Configuration.GetLogMaxSize()
        backup_count = Configuration.GetLogBackupCount()
    else:
        log_filename = None

    app_logger = logging.getLogger( GetProgramName() )

    # Tab-separated fields
    formatter = logging.Formatter( '%(asctime)s %(levelname)s: %(message)s' )

    if log_filename != None:
        # Rotate file based on size
        handler = logging.handlers.RotatingFileHandler( log_filename, maxBytes = max_size,
                                                        backupCount = backup_count, delay = True )
        handler.setFormatter( formatter )
        handler.setLevel( log_lvl )
    else:
        handler = logging.NullHandler()
        logging.critical( "No log handler" )
    app_logger.addHandler( handler )
    app_logger.setLevel( log_lvl )
