# -*- coding: utf-8 -*-

import wx
from wx import xrc
# TODO configuration

class AuthFrame( wx.Frame ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PreFrame()
        self.PostCreate( pre )
        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.visible_entries = 2
        self.max_entry_height = 0
        self.max_entry_width = 0
        self.res = wx.GetApp().res
        self.SetTitle( 'PyAuth' )

        # Locate and save references to important GUI elements
        self.auth_window = xrc.XRCCTRL( self, 'codes_window' )
        self.auth_container = self.auth_window.GetSizer()
        self.entries = self.populate_container()
        self.auth_window.SetScrollRate( 0, 1 )

        window_size = self.auth_window.GetSize()
        window_size.SetWidth( self.max_entry_width )
        window_size.SetHeight( self.visible_entries * self.max_entry_height )
        self.auth_window.SetVirtualSize( window_size )
        window_size.SetHeight( self.max_entry_height )
        self.auth_window.SetMinClientSize( window_size )
        self.auth_window.FitInside()

        window_size.SetHeight( self.visible_entries * self.max_entry_height )
        self.SetClientSize( window_size )
        window_size.SetHeight( self.max_entry_height )
        self.SetMinClientSize( window_size )
        self.FitInside()

        self.Refresh()


    def populate_container( self ):
        entry_count = 0

        # TODO Populate container for real

        for n in range( 0, 3 ):
            item = self.create_item( n, "Provider", "Account" )

            #Calculate max entry panel height and width accounting for the border
            item_size = item.GetSize()
            if item_size.GetHeight() + 4 > self.max_entry_height:
                self.max_entry_height = item_size.GetHeight() + 4
            if item_size.GetWidth() + 4 > self.max_entry_width:
                self.max_entry_width = item_size.GetWidth() + 4

            self.auth_container.Add( item, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2 )
            entry_count += 1
        
        return entry_count


    def create_item( self, n, provider, account ):
        # Load new copy of item from XRC and set it's real name
        item = self.res.LoadPanel( self.auth_window, 'entry_panel' )
        item.SetName( 'entry_panel_%s' % n )

        # TODO Load provider, account and dummy code

        # Set minimum size correctly
        s = item.GetSize()
        item.SetMinSize( s )

        return item
