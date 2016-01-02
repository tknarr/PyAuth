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
    c = GetPeggedCorner()
    if c in { 'TL', 'TR', 'BL', 'BR' }:
        r = ConvertPeggedToScreen( c, x, y )
        x = r[0]
        y = r[1]
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
    x = wp.x
    y = wp.y
    c = corner.upper()
    if c in { 'TL', 'TR', 'BL', 'BR' }:
        r = ConvertScreenToPegged( x, y, c )
        c = r[0]
        x = r[1]
        y = r[2]
    else:
        c = 'XX'
    if x >= 0:
        wx.Config.Get().WriteInt( '/window/last_x', x )
    if y >= 0:
        wx.Config.Get().WriteInt( '/window/last_y', y )
    wx.Config.Get().Write( '/window/pegged_corner', c )

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

def GetShowToolbar():
    return wx.Config.Get().ReadBool( '/window/show_toolbar', True )

def SetShowToolbar( state ):
    wx.Config.Get().WriteBool( '/window/show_toolbar', state )

def GetUseTaskbarIcon():
    return wx.Config.Get().ReadBool( '/window/use_taskbar_icon', False )

def SetUseTaskbarIcon( state ):
    wx.Config.Get().WriteBool( '/window/use_taskbar_icon', state )

def GetIconSet():
    return wx.Config.Get().Read( '/window/icon_set', 'white' )

def SetIconSet( setname ):
    wx.Config.Get().Write( '/window/icon_set', setname )

def GetToolIconSize():
    size_string = wx.Config.Get().Read( '/window/tool_icon_size', 'default' )
    s = wx.DefaultSize
    if size_string == 'small':
        s = wx.Size( 16, 16 )
    elif size_string == 'medium':
        s = wx.Size( 24, 24 )
    elif size_string == 'large':
        s = wx.Size( 32, 32 )
    elif size_string == 'extra-large':
        s = wx.Size( 48, 48 )
    elif size_string == 'default':
        s = wx.DefaultSize
    else:
        logging.warning( "Tool icon size not legal, resetting to default size." )
        wx.Config.Get().Write( '/window/tool_icon_size', 'default' )
        s = wx.DefaultSize
    return s

def SetToolIconSize( s ):
    if s.GetWidth() != s.GetHeight():
        logging.warning( "Tool icon width and height not equal: %s", str( s ) )
    x = s.GetWidth()
    if x != 16 and x != 24 and x != 32 and x != 48 and x != wx.DefaultSize.GetWidth():
        logging.warning( "Tool icon size not standard, using default size." )
        x = -1
    size_string = 'default'
    if x == 16:
        size_string = 'small'
    elif x == 24:
        size_string = 'medium'
    elif x == 32:
        size_string = 'large'
    elif x == 48:
        size_string = 'extra-large'
    wx.Config.Get().Write( '/window/tool_icon_size', size_string )

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


def ConvertScreenToPegged( x_pos, y_pox, corner = 'XX' ):
    # If corner is TL/BL/TR/BR then the screen coordinates are converted to pegged-relative
    # offsets from the given corner of the screen to the matching corner of the frame.
    # Otherwise an appropriate corner is determined based on what quarter of the screen
    # the centerpoint of the frame is in (ie. it will peg to the corner nearest the
    # matching corner of the frame).
    # The result is a tuple ( corner, x, y )
    
    scr_x = wx.SystemSettings.GetMetric( wx.SYS_SCREEN_X )
    scr_y = wx.SystemSettings.GetMetric( wx.SYS_SCREEN_Y )
    s = wx.GetApp().frame.GetSize()
    fr_w = s.GetWidth()
    fr_h = s.GetHeight()

    peg_corner = corner.upper()

    # If we weren't told the corner to peg to, calculate centerpoints and
    # see which quarter of the screen the frame centerpoint is in.
    if peg_corner not in { 'TL', 'TR', 'BL', 'BR' }:
        scr_center_x = scr_x / 2
        scr_center_y = scr_y / 2
        fr_center_x = x_pos + ( fr_w / 2 )
        fr_center_y = y_pos + ( fr_h / 2 )
        peg_corner = 'TL'
        if fr_center_x > scr_center_x:
            peg_corner[1] = 'R'
        if fr_center_y > scr_center_y:
            peg_corner[0] = 'B'

    # Start with TL
    peg_x = x_pos
    peg_y = y_pos
    # For B or R, adjust the y or x offset accordingly
    if peg_corner[1] == 'R':
        peg_x = scr_x - x_pos - fr_w
    if peg_corner[0] == 'B':
        peg_y = scr_y - y_pos - fr_h
            
    return ( peg_corner, peg_x, peg_y )

def ConvertPeggedToScreen( corner, x_offset, y_offset ):
    # Reverses the calculations in ConvertScreenToPegged()
    # The result is a tuple ( x, y ) giving screen coordinates for the frame's top-left corner

    scr_x = wx.SystemSettings.GetMetric( wx.SYS_SCREEN_X )
    scr_y = wx.SystemSettings.GetMetric( wx.SYS_SCREEN_Y )
    s = wx.GetApp().frame.GetSize()
    fr_w = s.GetWidth()
    fr_h = s.GetHeight()

    x_pos = x_offset
    y_pos = y_offset
    peg_corner = corner.upper()

    if peg_corner[1] == 'R':
        x_pos = scr_x - x_offset - fr_w
    if peg_corner[0] == 'B':
        y_pos = scr_y - y_offset - fr_h

    return ( x_pos, y_pos )
