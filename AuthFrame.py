# -*- coding: utf-8 -*-

import wx
from wx import xrc
import Configuration

class AuthFrame( wx.Frame ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PreFrame()
        self.PostCreate( pre )

        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.scrollbar_width = 0
        self.visible_entries = 2
        self.max_entry_height = 0
        self.max_entry_width = 0
        self.res = wx.GetApp().res

        self.SetTitle( 'PyAuth' )
        # TODO Restore last window size
        # TODO Restore last window position

        # Locate and save references to important GUI elements
        self.auth_window = xrc.XRCCTRL( self, 'codes_window' )
        self.auth_container = self.auth_window.GetSizer()
        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.auth_window )

        self.entries = self.populate_container()
        self.auth_window.SetScrollRate( 0, self.max_entry_height )

        self.AdjustWindowSizes()
        self.Refresh()


    def UpdateEntrySize( self, size ):
        changed = False
        if size.GetHeight() + 4 > self.max_entry_height:
            self.max_entry_height = size.GetHeight() + 4
            changed = True
        if size.GetWidth() + 4 > self.max_entry_width:
            self.max_entry_width = size.GetWidth() + 4
            changed = True
        if changed:
            self.AdjustWindowSizes()
            self.Refresh()


    def AdjustWindowSizes( self ):
        # Start with auth entry window size
        window_size = self.auth_window.GetSize()
        # Account for the scrollbar in the width
        window_size.SetWidth( self.max_entry_width + self.scrollbar_width )

        # Min client size of auth entry window should be 1 entry wide by 1 entry high
        window_size.SetHeight( self.max_entry_height )
        self.auth_window.SetMinClientSize( window_size )

        # Frame should be 1 entry wide, 1 entry high min and visible number high current
        window_size.SetHeight( self.visible_entries * self.max_entry_height )
        self.SetClientSize( window_size )
        window_size.SetHeight( self.max_entry_height )
        self.SetMinClientSize( window_size )
            

    def populate_container( self ):
        entry_count = 0

        # TODO Populate container for real

        # Create dummy entries
        for n in range( 1, 13 ):
            item = self.create_item( n, "Provider %s" % str(n), "Account %s" % str(n) )

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

        item.SetProvider( provider )
        item.SetAccount( account )

        # Set minimum size correctly
        s = item.GetSize()
        item.SetMinSize( s )

        return item
