# -*- coding: utf-8 -*-

import wx
from wx import xrc as xrc
from AuthenticationStore import AuthenticationEntry

class AuthEntryPanel( wx.Panel ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        p = wx.PrePanel()

        self.entry = None
        self.index = 0
        self.code = ''
        self.panel_size = wx.DefaultSize
        self.label_panel_size = wx.DefaultSize
        self.code_size = wx.DefaultSize

        self.label_panel = None
        self.provider_text = None
        self.account_text = None
        self.code_panel = None
        self.code_text = None
        self.timer_panel = None
        self.timer_gauge = None

        self.PostCreate( p )
        self.Bind( self._first_event_type, self.OnCreate )


    def _post_init( self ):
        self.label_panel = xrc.XRCCTRL( self, 'label_panel' )
        self.provider_text = xrc.XRCCTRL( self, 'provider_text' )
        self.account_text = xrc.XRCCTRL( self, 'account_text' )
        self.code_panel = xrc.XRCCTRL( self, 'code_panel' )
        self.code_text = xrc.XRCCTRL( self, 'code_text' )
        self.timer_panel = xrc.XRCCTRL( self, 'timer_panel' )
        self.timer_gauge = xrc.XRCCTRL( self, 'timer' )

        self.code_size = self.code_text.GetTextExtent( " 000000 " )
        self.code_text.SetSize( self.code_size )
        self.code_text.SetMinSize( self.code_size )
        self.code_panel.SetSize( self.code_size )
        self.code_panel.SetMinSize( self.code_size )
        
        self.ChangeContents()


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )
        self._post_init()
        self.Refresh


    def GetEntry( self ):
        return self.entry

    def SetEntry( self, entry ):
        self.entry = entry
        self.SetName( 'entry_panel_%s' % self.entry.GetGroup() )
        self.index = self.entry.GetSortIndex()
        self.code = self.entry.GenerateNextCode()


    def GetPanelSize( self ):
        return self.panel_size
    
    def GetLabelPanelSize( self ):
        return self.label_panel_size


    def ResizePanel( self, panel_size, label_panel_size ):
        self.label_panel_size = label_panel_size
        self.label_panel.SetSize( self.label_panel_size )
        self.label_panel.SetMinSize( self.label_panel_size )
        # TODO Lay out label panel contents

        self.panel_size = panel_size
        self.SetSize( self.panel_size )
        self.SetMinSize( self.panel_size )
        # TODO Lay out panel contents


    def ChangeContents( self ):
        self.code_text.SetLabelText( self.code )
        self.provider_text.SetLabelText( self.entry.GetProvider() )
        self.provider_text.SetMinSize( self.provider_text.GetSize() )
        self.account_text.SetLabelText( self.entry.GetAccount() )
        self.account_text.SetMinSize( self.account_text.GetSize() )
        # TODO Fit label panel to contents
        # TODO Fit panel to contents
        self.label_panel_size = self.label_panel.GetSize()
        self.panel_size = self.GetSize()

    def UpdateContents( self ):
        self.ChangeContents()
        gp = self.GetGrandParent()
        if gp != None:
            gp.UpdatePanelSize()
