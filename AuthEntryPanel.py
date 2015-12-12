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
        self.code = "000000"
        self.entry = None

        self.have_controls = False
        self.label_panel = None
        self.provider_ctrl = None
        self.account_ctrl = None
        self.code_panel = None
        self.code_ctrl = None
        self.timer_ctrl = None

        self.code_minsize = wx.Size()

        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.label_panel = xrc.XRCCTRL( self, "label_panel" )
        self.provider_ctrl = xrc.XRCCTRL( self, "provider_text" )
        self.account_ctrl = xrc.XRCCTRL( self, "account_text" )
        self.code_panel = xrc.XRCCTRL( self, "code_panel" )
        self.code_ctrl = xrc.XRCCTRL( self, "code_text" )
        self.timer_ctrl = xrc.XRCCTRL( self, "timer" )
        self.have_controls = True

        tx = self.code_ctrl.GetTextExtent( " 000000 " )
        self.code_minsize = wx.Size( tx[0], tx[1] )
        self.code_ctrl.SetMinSize( tx )
        self.code_ctrl.SetSize( tx )
        self.code_panel.SetMinSize( tx )
        self.code_panel.SetSize( tx )
        self.timer_ctrl.SetMinSize( self.timer_ctrl.GetSize() )
        
        self.UpdateContents()
        sx = self.AdjustSize()
        p = self.GetGrandParent()
        if p != None:
            p.UpdateEntrySize( sx )
        self.Refresh()


    def GetEntry( self ):
        return self.entry

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
        self.Refresh()


    def UpdateContents( self ):
        if self.entry != None and self.have_controls:
            self.provider_ctrl.SetLabelText( self.entry.provider )
            self.account_ctrl.SetLabelText( self.entry.account )
            self.code_ctrl.SetLabelText( self.code )


    def AdjustSize( self, sx = None ):
        if sx == None:
            sx = self.GetBestSize()
        self.SetSize( sx )
        self.SetMinSize( sx )
        if self.have_controls:
            csx = self.code_ctrl.GetSize()
            if csx.GetWidth() < self.code_minsize.GetWidth() or csx.GetHeight() < self.code_minsize.GetHeight():
                self.code_ctrl.SetSize( self.code_minsize )
                self.code_panel.SetSize( self.code_minsize )
            self.code_panel.GetSizer().Fit( self.code_panel )
            self.label_panel.GetSizer().Fit( self.label_panel )
        self.GetSizer().Fit( self )
        self.Refresh()
        return sx
