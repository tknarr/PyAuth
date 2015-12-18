# -*- coding: utf-8 -*-

# ${HOME}/.PyAuth/ - configuration directory
#   config.cfg - configuration
#   database.cfg - authorization secrets storage

# Config items:
#   Last number of visible items in window
#   Last window position
#   Peg to top-left, top-right, bottom-left, bottom-right corner (TL, TR, BL, BR, or XX for not pegged)
#       The last window position is in screen coordinates when not pegged to a corner.
#       When pegged, it's a delta from the pegged corner of the display to the same corner of the window.
#   Number of items shown
#   Last auth secrets file
#   Show timers
#   Show codes for all entries
#   Database filename
#   Logging level name, will be converted to the correct value for use

import logging
import wx

def Save():
    wx.Config.Get().Flush()

def GetLastWindowPosition():
    x = wx.Config.Get().ReadInt( '/window/last_x', -1 )
    y = wx.Config.Get().ReadInt( '/window/last_y', -1 )
    # TODO Convert from pegged-relative to screen position, needs window size to calculate
    wp = None
    if x >= 0 and y >= 0:
        wp = wx.Point( x, y )
    return wp

def GetPeggedCornerPosition():
    x = wx.Config.Get().ReadInt( '/window/last_x', -1 )
    y = wx.Config.Get().ReadInt( '/window/last_y', -1 )
    wp = None
    if x >= 0 and y >= 0:
        wp = wx.Point( x, y )
    return wp

def GetPeggedCorner():
    return wx.Config.Get().Read( '/window/pegged_corner', 'XX' )

def SetLastWindowPosition( wp, corner = 'XX' ):
    # TODO Convert to pegged-relative if corner not XX or TL, needs window size to calculate
    if wp.x >= 0:
        wx.Config.Get().WriteInt( '/window/last_x', wp.x )
    if wp.y >= 0:
        wx.Config.Get().WriteInt( '/window/last_y', wp.y )
    wx.Config.Get().Write( '/window/pegged_corner', corner.upper() )

def GetNumberOfItemsShown():
    return wx.Config.Get().ReadInt( '/window/items_shown', 2 )

def SetNumberOfItemsShown( n ):
    wx.Config.Get().WriteInt( '/window/items_shown', n )

def GetShowTimers():
    return wx.Config.Get().ReadBool( '/window/show_timers', True )

def SetShowTimers( state ):
    wx.Config.Get().WriteBool( '/window/show_timers', state )

def GetShowAllCodes():
    return wx.Config.Get().ReadBool( '/window/show_all_codes', True )

def SetShowAllCodes( state ):
    wx.Config.Get().WriteBool( '/window/show_all_codes', state )

def GetDatabaseFilename():
    return wx.Config.Get().Read( '/database/file_name', 'database.cfg' )

def GetLoggingLevel():
    level_string = wx.Config.Get().Read( '/logging/level', 'WARNING' )
    loglevel = getattr( logging, level_string.upper(), None )
    if not isinstance( loglevel, int ):
        logging.warning( "Invalid logging level %s, using WARNING instead", level_string )
        loglevel = logging.WARNING
    return loglevel

def GetLogFilename():
    return wx.Config.Get().Read( '/logging/filename' )
