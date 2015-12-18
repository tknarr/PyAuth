# -*- coding: utf-8 -*-

import logging
import Configuration

mylogger = logging.GetLogger()

def Init():
    loglevel = Configuration.GetLoggingLevel()
    logfile = Configureation.GetLogFilename()

    l = logging.GetLogger( 'PyAuth' )
    h = None
    if logfile != None and logfile != '':
        h = logging.FileHandler( logfile)
    else:
        h = logging.StreamHandler()
    l.addHandler( h )
    l.SetLevel( loglevel )

    mylogger = l
