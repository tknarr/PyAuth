# -*- coding: utf-8 -*-

import wx

class AuthCodeText( wx.StaticText ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PreStaticText()
        self.PostCreate( pre )
        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.Refresh()

                
     # TODO Auth code text class
