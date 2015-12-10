# -*- coding: utf-8 -*-

# ${HOME}/.PyAuth/ - configuration directory
#   config.cfg - configuration
#   database.cfg - authorization secrets storage

# Config items:
#   Last window size
#   Last window position
#   Peg to top-left, top-right, bottom-left, bottom-right corner (TL, TR, BL, BR, or XX for not pegged)
#   Number of items shown
#   Last auth secrets file
#   Show timers
#   Show codes for all entries

import wx

def GetAppConfigName():
    # TODO Use .PyAuth or PyAuth depending on OS
    return ".PyAuth"

def GetLastWindowSize():
    w = wx.Config.Get().ReadInt( "/window/last_width", -1 )
    h = wx.Config.Get().ReadInt( "/window/last_height", -1 )
    ws = None
    if w > 0 and h > 0:
        ws = wx.Size( w, h )
    return ws

def SetLastWindowSize( ws ):
    if ws.GetWidth() > 0:
        wx.Config.Get().WriteInt( "/window/last_width", ws.GetWidth() )
    if wx.GetHeight() > 0:
        wx.Config.Get().WriteInt( "/window/last_height", ws.GetHeight() )

def GetLastWindowPosition():
    x = wx.Config.Get().ReadInt( "/window/last_x", -1 )
    y = wx.Config.Get().ReadInt( "/window/last_y", -1 )
    wp = None
    if x >= 0 and y >= 0:
        wp = wx.Point( x, y )
    return wp

def SetLastWindowPosition( wp ):
    if wp.x >= 0:
        wx.Config.Get().WriteInt( "/window/last_x", wp.x )
    if wp.y >= 0:
        wx.Config.Get().WriteInt( "/window/last_x", wp.y )

def GetPeggedCorner():
    return wx.Config.Get().Read( "/window/pegged_corner", "XX" )

def SetPeggedCorner( corner ):
    s = corner.upper()
    wx.Config.Get().Write( "/window_pegged_corner", s )

def GetNumberOfItemsShown():
    return wx.Config.Get().ReadInt( "/window/items_shown", 1 )

def SetNumberOfItemsShown( n ):
    wx.Config.Get().WriteInt( "/window/items_shown", n )

def GetShowTimers():
    return wx.Config.Get().ReadBool( "/window/show_timers", True )

def SetShowTimers( state ):
    wx.Config.Get().WriteBool( "/window/show_timers", state )

def GetShowAllCodes():
    return wx.Config.Get().ReadBool( "/window/show_all_codes", True )

def SetShowAllCodes( state ):
    wx.Config.Get().WriteBool( "/window/show_all_codes", state )

def GetDatabaseDirectory():
    return wx.Config.Get().Read( "/database/directory", wx.StandardPaths.Get().GetUserConfigDir() + "/.PyAuth" )

def GetDatabaseFilename():
    return wx.Config.Get().Read( "/database/file_name", "database.cfg" )

def GetDatabasePath():
    return GetDatabaseDirectory() + "/" + GetDatabaseFilename()
