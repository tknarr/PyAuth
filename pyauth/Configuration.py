# -*- coding: utf-8 -*-
"""
Configuration routines.

${HOME}/.PyAuth/ - configuration directory
    pyauth.cfg - configuration data
    database.cfg - authorization secrets storage

Config items:
    Last window position
    Last window size
    Peg to top-left, top-right, bottom-left, bottom-right corner (TL, TR, BL, BR, or XX for not pegged)
        The last window position is in screen coordinates when not pegged to a corner.
        When pegged, it's a delta from the pegged corner of the display to the same corner of the window.
    Last number of visible items in window
    Start minimized flag
    Show timers
    Show codes for all entries
    Show toolbar flag
    Use notification tray flag
    Icon set name
    Toolbar icon size setting
    Database filename
    Logging level name
    Log file name
    Log file maximum size
    Log file backup count
    Remembered toolbar height
    QR code box size
"""

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

import logging
import os.path
import wx


def Save():
    """Force save of configuration to disk."""
    wx.Config.Get().Flush()


def GetLastWindowPosition():
    x = wx.Config.Get().ReadInt('/window/last_x', -1)
    y = wx.Config.Get().ReadInt('/window/last_y', -1)
    c = GetPeggedCorner()
    if c in {'TL', 'TR', 'BL', 'BR'}:
        r = ConvertPeggedToScreen(c, x, y)
        x = r[0]
        y = r[1]
    wp = None
    if x >= 0 and y >= 0:
        wp = wx.Point(x, y)
    return wp


def GetPeggedCornerPosition():
    """Return remembered window corner position."""
    x = wx.Config.Get().ReadInt('/window/last_x', -1)
    y = wx.Config.Get().ReadInt('/window/last_y', -1)
    wp = None
    if x >= 0 and y >= 0:
        wp = wx.Point(x, y)
    return wp


def GetPeggedCorner():
    """Return which corner the position is pegged to."""
    return wx.Config.Get().Read('/window/pegged_corner', 'XX')


def SetLastWindowPosition(wp, corner = 'XX'):
    """Save the last window position and pegged corner."""
    x = wp.x
    y = wp.y
    c = corner.upper()
    if c in {'TL', 'TR', 'BL', 'BR'}:
        r = ConvertScreenToPegged(x, y, c)
        c = r[0]
        x = r[1]
        y = r[2]
    else:
        c = 'XX'
    if x >= 0:
        wx.Config.Get().WriteInt('/window/last_x', x)
    if y >= 0:
        wx.Config.Get().WriteInt('/window/last_y', y)
    wx.Config.Get().Write('/window/pegged_corner', c)


def GetLastWindowSize():
    """Return remembered window size."""
    x = wx.Config.Get().ReadInt('/window/width', -1)
    y = wx.Config.Get().ReadInt('/window/height', -1)
    ws = None
    if x >= 0 and y >= 0:
        ws = wx.Size(x, y)
    return ws


def SetLastWindowSize(ws):
    """Save last window size."""
    x = ws.x
    y = ws.y
    if x >= 0:
        wx.Config.Get().WriteInt('/window/width', x)
    if y >= 0:
        wx.Config.Get().WriteInt('/window/height', y)


def GetStartMinimized():
    """Return whether or not to start minimized."""
    return wx.Config.Get().ReadBool('/window/start_minimized', False)


def SetStartMinimized(state):
    """Set whether or not to start minimized."""
    wx.Config.Get().WriteBool('/window/start_minimized', state)


def GetNumberOfItemsShown():
    """Return last number of items visible in window."""
    return wx.Config.Get().ReadInt('/window/items_shown', 2)


def SetNumberOfItemsShown(n):
    """Set last number of items visible in window."""
    wx.Config.Get().WriteInt('/window/items_shown', n)


def GetShowTimers():
    """Return show-timers flag."""
    return wx.Config.Get().ReadBool('/window/show_timers', True)


def SetShowTimers(state):
    """Set show-timers flag state."""
    wx.Config.Get().WriteBool('/window/show_timers', state)


def GetShowAllCodes():
    """Return show-all-codes flag."""
    return wx.Config.Get().ReadBool('/window/show_all_codes', True)


def SetShowAllCodes(state):
    """Set show-all-codes flag state."""
    wx.Config.Get().WriteBool('/window/show_all_codes', state)


def GetShowToolbar():
    """Return show-toolbar flag."""
    return wx.Config.Get().ReadBool('/window/show_toolbar', True)


def SetShowToolbar(state):
    """Set show-toolbar flag state."""
    wx.Config.Get().WriteBool('/window/show_toolbar', state)


def GetToolbarHeight():
    """Return remembered toolbar height."""
    return wx.Config.Get().ReadInt('/window/toolbar_height', 0)


def SetToolbarHeight(h):
    """Set remembered toolbar height."""
    wx.Config.Get().WriteInt('/window/toolbar_height', h)


def GetUseTaskbarIcon():
    """Return use-notification-tray flag."""
    return wx.Config.Get().ReadBool('/window/use_taskbar_icon', False)


def SetUseTaskbarIcon(state):
    """Set use-notification-tray flag."""
    wx.Config.Get().WriteBool('/window/use_taskbar_icon', state)


def GetIconSet():
    """Return the current icon set name."""
    return wx.Config.Get().Read('/window/icon_set', 'white')


def SetIconSet(setname):
    """Set the name of the icon set to use."""
    wx.Config.Get().Write('/window/icon_set', setname)


def GetToolIconSize():
    """Return the current toolbar icon size."""
    size_string = wx.Config.Get().Read('/window/tool_icon_size', 'default')
    s = wx.DefaultSize
    if size_string == 'small':
        s = wx.Size(16, 16)
    elif size_string == 'medium':
        s = wx.Size(24, 24)
    elif size_string == 'large':
        s = wx.Size(32, 32)
    elif size_string == 'extra-large':
        s = wx.Size(48, 48)
    elif size_string == 'default':
        s = wx.DefaultSize
    else:
        logging.warning("Tool icon size not legal, resetting to default size.")
        wx.Config.Get().Write('/window/tool_icon_size', 'default')
        s = wx.DefaultSize
    return s


def SetToolIconSize(s):
    """Set the toolbar icon size."""
    if s.GetWidth() != s.GetHeight():
        logging.warning("Tool icon width and height not equal: %s", unicode(s))
    x = s.GetWidth()
    if x != 16 and x != 24 and x != 32 and x != 48 and x != wx.DefaultSize.GetWidth():
        logging.warning("Tool icon size not standard, using default size.")
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
    wx.Config.Get().Write('/window/tool_icon_size', size_string)


def GetConfigDirectory():
    """Return the configuration directory path."""
    cfgfile = wx.FileConfig.GetLocalFileName('pyauth.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR)
    cfgdir = os.path.dirname(cfgfile)
    return cfgdir


def GetDatabaseFilename():
    """Return the authentication secrets database filename."""
    return wx.Config.Get().Read('/database/file_name', 'database.cfg')


def GetLoggingLevel():
    """Return the current logging level."""
    level_string = wx.Config.Get().Read('/logging/level', 'warning')
    loglevel = getattr(logging, level_string.upper(), None)
    if not isinstance(loglevel, int):
        logging.warning("Invalid logging level %s, using WARNING instead", level_string)
        loglevel = logging.WARNING
    return loglevel


def GetLogFilename():
    """Return the name of the log file."""
    return wx.Config.Get().Read('/logging/filename', GetConfigDirectory() + "/errors.log")


def GetLogMaxSize():
    """Return the log file maximum size."""
    return wx.Config.Get().ReadInt('/logging/max_size', 1024 * 1024)


def GetLogBackupCount():
    """Return the log file backup count."""
    return wx.Config.Get().ReadInt('/logging/backup_count', 5)


def GetQRBoxSize():
    """Return the size of the QR code dots in pixels."""
    return wx.Config.Get().ReadInt('/qr_code/box_size', 4)


def SetQRBoxSize(x):
    """Set the size of a QR code dot in pixels."""
    wx.Config.Get().WriteInt('/qr_code/box_size', x)


def ConvertScreenToPegged(x_pos, y_pos, corner = 'XX'):
    """
    Convert screen coordinates to relative-to-pegged-corner.

    If corner is TL/BL/TR/BR then the screen coordinates are converted to pegged-relative
    offsets from the given corner of the screen to the matching corner of the frame.
    Otherwise an appropriate corner is determined based on what quarter of the screen
    the centerpoint of the frame is in (ie. it will peg to the corner nearest the
    matching corner of the frame).
    The result is a tuple ( corner, x, y )
    """

    scr_x = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
    scr_y = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
    s = wx.GetApp().frame.GetSize()
    fr_w = s.GetWidth()
    fr_h = s.GetHeight()

    peg_corner = corner.upper()

    # If we weren't told the corner to peg to, calculate centerpoints and
    # see which quarter of the screen the frame centerpoint is in.
    if peg_corner not in {'TL', 'TR', 'BL', 'BR'}:
        scr_center_x = scr_x / 2
        scr_center_y = scr_y / 2
        fr_center_x = x_pos + (fr_w / 2)
        fr_center_y = y_pos + (fr_h / 2)
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

    return (peg_corner, peg_x, peg_y)


def ConvertPeggedToScreen(corner, x_offset, y_offset):
    """
    Convert relative-to-pegged-corner coordinates to screen coordinates.

    Reverses the calculations in ConvertScreenToPegged()
    The result is a tuple ( x, y ) giving screen coordinates for the frame's top-left corner
    """

    scr_x = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
    scr_y = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
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

    return (x_pos, y_pos)
