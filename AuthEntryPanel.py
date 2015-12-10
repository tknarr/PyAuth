# -*- coding: utf-8 -*-

import wx
from wx import xrc

class AuthEntryPanel( wx.Panel ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PrePanel()
        self.PostCreate( pre )

        self.index = 0
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
        p = self.GetGrandParent()
        if p != None:
            p.UpdateEntrySize( sx )

    def SetIndex( self, i ):
        self.index = i
        self.SetName( "entry_panel_%s" % str(i) )
            
    def SetProvider( self, s ):
        self.provider = s

    def SetAccount( self, s ):
        self.account = s

    def SetCode( self, s ):
        self.code = s


    def AdjustSize( self, sx ):
        self.SetSize( sx )
        self.SetMinSize( sx )
