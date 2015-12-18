# -*- coding: utf-8 -*-

import logging
import Configuration

mylogger = logging.getLogger()

def Init():
    loglevel = Configuration.GetLoggingLevel()
    logfile = Configuration.GetLogFilename()

    l = logging.getLogger( 'PyAuth' )
    h = None
    if logfile != None and logfile != '':
        h = logging.FileHandler( logfile)
    else:
        h = logging.StreamHandler()
    l.addHandler( h )
    l.setLevel( loglevel )

    mylogger = l
