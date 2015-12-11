# -*- coding: utf-8 -*-

import wx
from wx import xrc
import AuthenticationStore

class AuthEntryPanel( wx.Panel ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PrePanel()
        self.PostCreate( pre )

        self.index = 0
        self.code = " 000000 "
        self.entry = None

        self.provider_ctrl = None
        self.account_ctrl = None
        self.code_ctrl = None
        self.timer_ctrl = None

        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.provider_ctrl = xrc.XRCCTRL( self, "provider_text" )
        self.account_ctrl = xrc.XRCCTRL( self, "account_text" )
        self.code_ctrl = xrc.XRCCTRL( self, "code_text" )
        self.timer_ctrl = xrc.XRCCTRL( self, "timer" )

        self.UpdateContents()
        sx = self.AdjustSize()
        p = self.GetGrandParent()
        if p != None:
            p.UpdateEntrySize( sx )


    def SetEntry( self, entry ):
        self.entry = entry
        self.SetName( "entry_panel_%s" % str(entry.entry_group) )
        self.index = entry.sort_index
        self.code = entry.GenerateNextCode()
        self.UpdateContents()
        sx = self.AdjustSize()
        p = self.GetGrandParent()
        if p != None:
            p.UpdateEntrySize( sx )


    def UpdateContents( self ):
        if self.entry != None:
            if self.provider_ctrl != None:
                self.provider_ctrl.SetLabelText( self.entry.provider )
            if self.account_ctrl != None:
                self.account_ctrl.SetLabelText( self.entry.account )
            if self.code_ctrl != None:
                self.code_ctrl.SetLabelText( self.code )


    def AdjustSize( self, sx = None ):
        if sx == None:
            sx = self.GetBestSize()
        self.SetSize( sx )
        self.SetMinSize( sx )
        return sx
