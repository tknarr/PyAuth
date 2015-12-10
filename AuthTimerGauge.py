# -*- coding: utf-8 -*-

import wx

class AuthTimerGauge( wx.Gauge ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PreGauge()
        self.PostCreate( pre )

        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.Refresh()

        
    # TODO Timer bar, derives from wx class
