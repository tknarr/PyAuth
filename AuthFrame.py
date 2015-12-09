# -*- coding: utf-8 -*-

import wx
from wx import xrc
# TODO configuration

class AuthFrame( wx.Frame ):

    ##_first_event_type = wx.EVT_WINDOW_CREATE
    _first_event_type = wx.EVT_SIZE

    def __init__( self ):
        pre = wx.PreFrame()
        self.PostCreate( pre )
        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.res = wx.GetApp().res
        self.SetTitle( 'PyAuth' )

        # Locate and save references to important GUI elements
        self.auth_window = xrc.XRCCTRL( self, 'codes_window' )
        self.auth_container = self.auth_window.GetSizer()
        self.entries = self.populate_container()
        self.auth_container.Fit( self.auth_window )

        self.SetClientSize( self.auth_window.GetSize() )
        # TODO Set scrollbars properly

        self.Refresh()


    def populate_container( self ):
        entry_count = 0

        # TODO Populate container for real

        # Populate container with dummy entry
        item = self.res.LoadPanel( self.auth_window, 'entry_panel' )
        item.SetName( 'entry_panel_0' )
        # Set minimum size correctly
        s = item.GetSize()
        item.SetMinSize( s )
        self.auth_container.Add( item, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2 )

        #return entry_count
        return 1


    def create_item( self, n, provider, account ):
        # Load new copy of item from XRC and set it's real name
        item = self.res.LoadPanel( self.auth_window, 'entry_panel' )
        item.SetName( 'entry_panel_%s' % n )

        # TODO Load provider, account and dummy code
        # TODO Set initial gauge position = current Unix time mod 30 seconds

        # Set minimum size correctly
        s = item.GetSize()
        item.SetMinSize( s )

        return item
