# -*- coding: utf-8 -*-

import wx
from wx import xrc as xrc
import Configuration
from AuthenticationStore import AuthenticationStore, AuthenticationEntry as AuthenticationEntry
from AuthEntryPanel import AuthEntryPanel as AuthEntryPanel

class AuthFrame( wx.Frame ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        wx.PreFrame()

        self.res = wx.GetApp().res
        self.entries_window = None
        self.auth_store = None
        self.entry_panels = []
        self.visible_entries = 0
        self.entry_size = wx.Size( 0, 0 ) # Longest size in each direction of any entry panel
        self.label_size = wx.Size( 0, 0 ) # Longest size in each direction of any label panel

        # Internal values
        self.entry_border = 2
        self.scrollbar_width = 0

        self.PostCreate( p )
        self.Bind( self._first_event_type, self.OnCreate )


    def _post_init( self ):
        self.entries_window = xrc.XRCCTRL( self, 'entries_window' )
        self.auth_store = AuthenticationStore( Configuration.GetDatabaseFilename() )

        # Get scrollbar width so we can account for it in window sizing
        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.entries_window )
        
        # Create our entry item panels and put them in the scrollable window
        self.entry_panels = []
        for entry in self.auth_store.EntryList():
            panel = self.res.LoadPanel( self, 'entry_panel' )
            panel.SetEntry( entry )
            self.entry_panels.append( panel )
        auth_container = self.entries_window.GetSizer()
        for item in self.entry_panels:
            auth_container.Add( item, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 2 )

        # TODO Fit/Layout

        # Window event handlers
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        # Menu event handlers
        menu_bar = xrc.XRCCTRL( self, 'menu_bar' )
        self.Bind( wx.EVT_MENU, self.OnMenuNewEntry,     xrc.XRCID( menu_bar, 'NEW' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuQuit,         xrc.XRCID( menu_bar, 'QUIT' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuEditEntry,    xrc.XRCID( menu_bar, 'EDIT' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuDeleteEntry,  xrc.XRCID( menu_bar, 'DELETE' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuMoveUp,       xrc.XRCID( menu_bar, 'MOVE_UP' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuMoveDown,     xrc.XRCID( menu_bar, 'MOVE_DOWN' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuShowTimers,   xrc.XRCID( menu_bar, 'SHOW_TIMERS' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuShowAllCodes, xrc.XRCID( menu_bar, 'SHOW_ALL_CODES' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuHelpContents, xrc.XRCID( menu_bar, 'HELP' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuAbout,        xrc.XRCID( menu_bar, 'ABOUT' ) )


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )
        self._post_init()
        self.Refresh


    def OnCloseWindow( self, event ):
        self.auth_store.Save()
        wp = self.GetPosition()
        Configuration.SetLastWindowPosition( wp )
        items = self.CalcItemsShown()
        # TODO Remove this limit later
        if items > 12:
            items = 12
        Configuration.SetNumberOfItemsShown( items )
        Configuration.Save()
        self.Destroy()


    def OnMenuNewEntry( self, event ):
        # TODO menu handler
        print "New Entry"

    def OnMenuQuit( self, event ):
        self.Close()

    def OnMenuEditEntry( self, event ):
        # TODO menu handler
        print "Edit Entry"

    def OnMenuDeleteEntry( self, event ):
        # TODO menu handler
        print "Delete Entry"

    def OnMenuMoveUp( self, event ):
        # TODO menu handler
        print "Move Up"

    def OnMenuMoveDown( self, event ):
        # TODO menu handler
        print "Move Down"

    def OnMenuShowTimers( self, event ):
        # TODO menu handler
        print "Show Timers"

    def OnMenuShowAllCodes( self, event ):
        # TODO menu handler
        print "Show All Codes"

    def OnMenuHelpContents( self, event ):
        # TODO menu handler
        print "Help Contents"

    def OnMenuAbout( self, event ):
        # TODO menu handler
        print "About"


    def CalcItemsShown( self, ws ):
        ws = self.GetClientSize()
        # Doing integer math, so we can't cancel terms and add 1/2
        n = ws.GetHeight() + ( self.entry_size.GetHeight() + 2 * self.entry_border ) / 2
        d = self.entry_size.GetHeight() + 2 * self.entry_border
        return n / d


    def AdjustWindowSizes( self ):
        # Need to adjust this here, it depends on the entry height which may change
        self.entry_window.SetScrollRate( 0, self.entry_size.GetHeight() + 2 * self.entry_border )

        # Frame size is 1 entry wide accounting for scrollbar, visible_entries high
        client_size = wx.DefaultSize
        client_size.SetWidth( self.entry_size.GetWidth() + 2 * self.entry_border + self.scrollbar_width )
        client_size.SetHeight( self.visible_entries * ( self.entry_size.GetHeight() + 2 * self.entry_border ) )
        self.entry_window.SetSize( client_size )
        self.SetClientSize( client_size )

        # Minimum size is 1 entry wide accounting for scrollbar, 1 entry high
        min_size = wx.DefaultSize
        min_size.SetWidth( self.entry_size.GetWidth() + 2 * self.entry_border + self.scrollbar_width )
        min_size.SetHeight( self.entry_size.GetHeight() + 2 * self.entry_border )
        self.entry_window.SetMinSize( min_size )
        self.SetMinClientSize( min_size )

        # TODO Fit/Layout


    def AdjustPanelSizes( self ):
        self.entry_size = wx.Size( 0, 0 )
        for entry in self.entry_panels:
            # Update max entry panel sizes
            entry_size = entry.GetPanelSize()
            if entry_size.GetHeight() > self.entry_size.GetHeight():
                self.entry_size.SetHeight( entry_size.GetHeight() )
            if entry_size.GetWidth() > self.entry_size.GetWidth():
                self.entry_size.SetWidth( entry_size.GetWidth() )
            label_size = entry.GetLabelPanelSize()
            if label_size.GetHeight() > self.label_size.GetHeight():
                self.label_size.SetHeight( label_size.GetHeight() )
            if label_size.GetWidth() > self.label_size.GetWidth():
                self.label_size.SetWidth( label_size.GetWidth() )
        for entry in self.entry_panels:
            entry.ResizePanel( self.entry_size, self.label_size )

        # TODO Fit/Layout
                

    def UpdatePanelSize( self ):
        self.AdjustPanelSizes()
        self.AdjustWindowSizes()
        self.Refresh()
        self.SendSizeEvent()
        self.SafeYield()
