# -*- coding: utf-8 -*-

import wx
from wx import xrc

class AuthEntryPanel( wx.Panel ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PrePanel()
        self.PostCreate( pre )

        self.provider = ""
        self.account = ""
        self.code = " 000000 "

        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.provider_ctrl = xrc.XRCCTRL( self, "provider_text" )
        self.account_ctrl = xrc.XRCCTRL( self, "account_text" )
        self.code_ctrl = xrc.XRCCTRL( self, "code_text" )
        self.timer_ctrl = xrc.XRCCTRL( self, "timer" )

        self.provider_ctrl.SetLabelText( self.provider )
        self.account_ctrl.SetLabelText( self.account )
        self.code_ctrl.SetLabelText( self.code )

        sx = self.GetBestSize()
        self.SetSize( sx )
        self.SetMinSize( sx )


    def SetProvider( self, s ):
        self.provider = s

    def SetAccount( self, s ):
        self.account = s

    def SetCode( self, s ):
        self.code = s


    def AdjustSize( self, sx ):
        self.SetSize( sx )
        self.SetMinSize( sx )
