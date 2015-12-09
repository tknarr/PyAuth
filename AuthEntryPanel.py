# -*- coding: utf-8 -*-

import wx

class AuthEntryPanel( wx.Panel ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PrePanel()
        self.PostCreate( pre )
        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.provider_ctrl = None
        self.account_ctrl = None
        self.code_ctrl = None
        self.timer_ctrl = None
        
        self.Refresh()


    # TODO Auth code panel class
