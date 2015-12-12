# -*- coding: utf-8 -*-

import wx
from wx import xrc
import Configuration
import AuthenticationStore
from AuthenticationStore import AuthenticationStore

class AuthFrame( wx.Frame ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        pre = wx.PreFrame()
        self.PostCreate( pre )

        self.entries = 0
        
        self.Bind( self._first_event_type, self.OnCreate )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )

        self.scrollbar_width = 0
        self.visible_entries = Configuration.GetNumberOfItemsShown()
        self.max_entry_height = 0
        self.max_entry_width = 0
        self.res = wx.GetApp().res
        self.auth_store = AuthenticationStore( Configuration.GetDatabasePath() )

        self.SetTitle( 'PyAuth' )
        wp = Configuration.GetLastWindowPosition()
        if wp != None:
            self.SetPosition( wp )

        # Locate and save references to important GUI elements
        self.auth_window = xrc.XRCCTRL( self, 'codes_window' )
        self.auth_container = self.auth_window.GetSizer()
        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.auth_window )

        self.entries = self.populate_container()
        self.auth_window.SetScrollRate( 0, self.max_entry_height + 4 )

        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )

        self.AdjustWindowSizes()
        sx = wx.Size( self.max_entry_width, self.max_entry_height )
        children = self.auth_window.GetChildren()
        for panel in children:
            panel.AdjustSize( sx )
        self.auth_container.Fit( self.auth_window )
        self.Refresh()


    def OnCloseWindow( self, event ):
        self.auth_store.Save()
        wp = self.GetPosition()
        Configuration.SetLastWindowPosition( wp )
        ws = self.GetClientSize()
        items = ( ws.GetHeight() + ( self.max_entry_height / 2 ) ) / ( self.max_entry_height + 4 )
        Configuration.SetNumberOfItemsShown( items )
        Configuration.Save()
        self.Destroy()


    def UpdateEntrySize( self, size ):
        changed = True
        if size.GetHeight() > self.max_entry_height:
            self.max_entry_height = size.GetHeight()
            changed = True
        if size.GetWidth() > self.max_entry_width:
            self.max_entry_width = size.GetWidth()
            changed = True
        if changed:
            self.AdjustWindowSizes()
            sx = wx.Size( self.max_entry_width, self.max_entry_height )
            children = self.auth_window.GetChildren()
            for panel in children:
                panel.AdjustSize( sx )
        self.auth_container.Fit( self.auth_window )
        self.Refresh()


    def AdjustWindowSizes( self ):
        # Start with auth entry window size
        window_size = self.auth_window.GetSize()
        # Account for the scrollbar in the width
        window_size.SetWidth( self.max_entry_width + 4 + self.scrollbar_width )

        # Min client size of auth entry window should be 1 entry wide by 1 entry high
        window_size.SetHeight( self.max_entry_height + 4 )
        self.auth_window.SetMinClientSize( window_size )
        self.SetMinClientSize( window_size )

        # Frame client area should be 1 entry wide, 1 entry high min and visible number high current
        window_size.SetHeight( self.visible_entries * ( self.max_entry_height + 4 ) )
        self.auth_window.SetClientSize( window_size )
        self.SetClientSize( window_size )


    def populate_container( self ):
        entry_count = 0

        # Populate container from authentication store
        for entry in self.auth_store.EntryList():
            item = self.create_item( entry )

            #Calculate max entry panel height and width accounting for the border
            item_size = item.GetSize()
            if item_size.GetHeight() > self.max_entry_height:
                self.max_entry_height = item_size.GetHeight()
            if item_size.GetWidth() > self.max_entry_width:
                self.max_entry_width = item_size.GetWidth()

            self.auth_container.Add( item, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2 )
            entry_count += 1
        
        return entry_count


    def create_item( self, entry ):
        # Load new copy of item from XRC
        item = self.res.LoadPanel( self.auth_window, 'entry_panel' )
        item.SetEntry( entry )
        return item
