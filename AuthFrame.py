# -*- coding: utf-8 -*-

import logging
import wx
from wx import xrc as xrc
import Configuration
from AuthenticationStore import AuthenticationStore, AuthenticationEntry as AuthenticationEntry
from AuthEntryPanel import AuthEntryPanel as AuthEntryPanel

class AuthFrame( wx.Frame ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        p = wx.PreFrame()

        self.res = wx.GetApp().res
        self.entries_window = None
        self.auth_store = None
        self.entry_panels = []
        self.visible_entries = 0
        self.entry_size = wx.Size( 0, 0 ) # Longest size in each direction of any entry panel
        self.label_width = 0 # Longest width label

        # Internal values
        self.entry_border = 2
        self.scrollbar_width = 0

        self.PostCreate( p )
        self.Bind( self._first_event_type, self.OnCreate )


    def _post_init( self ):
        logging.debug( "AF  post-init" )
        self.entries_window = xrc.XRCCTRL( self, 'entries_window' )
        self.auth_store = AuthenticationStore( Configuration.GetDatabaseFilename() )

        # Get scrollbar width so we can account for it in window sizing
        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.entries_window )
        
        # Create our entry item panels and put them in the scrollable window
        self.entry_panels = []
        for entry in self.auth_store.EntryList():
            logging.debug( "AF  create panel: %d", entry.GetGroup() )
            panel = self.res.LoadPanel( self.entries_window, 'entry_panel' )
            panel.SetEntry( entry )
            self.entry_panels.append( panel )
        for panel in self.entry_panels:
            logging.debug( "AF  add panel:    %s", panel.GetName() )
            logging.debug( "AF  panel size %s min %s", str( panel.GetSize() ), str( panel.GetMinSize() ) )
            self.entries_window.GetSizer().Add( panel, flag = wx.ALL | wx.ALIGN_CENTER,
                                                border = self.entry_border )

        self.AdjustPanelSizes()
        self.AdjustWindowSizes()

        # Window event handlers
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        # Menu event handlers
        menu_bar = xrc.XRCCTRL( self, 'menu_bar' )
        self.Bind( wx.EVT_MENU, self.OnMenuNewEntry,     id = xrc.XRCID( 'NEW' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuQuit,         id = xrc.XRCID( 'QUIT' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuEditEntry,    id = xrc.XRCID( 'EDIT' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuDeleteEntry,  id = xrc.XRCID( 'DELETE' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuMoveUp,       id = xrc.XRCID( 'MOVE_UP' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuMoveDown,     id = xrc.XRCID( 'MOVE_DOWN' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuShowTimers,   id = xrc.XRCID( 'SHOW_TIMERS' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuShowAllCodes, id = xrc.XRCID( 'SHOW_ALL_CODES' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuHelpContents, id = xrc.XRCID( 'HELP' ) )
        self.Bind( wx.EVT_MENU, self.OnMenuAbout,        id = xrc.XRCID( 'ABOUT' ) )


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
        logging.warning( "New Entry" )

    def OnMenuQuit( self, event ):
        self.Close()

    def OnMenuEditEntry( self, event ):
        # TODO menu handler
        logging.warning( "Edit Entry" )

    def OnMenuDeleteEntry( self, event ):
        # TODO menu handler
        logging.warning( "Delete Entry" )

    def OnMenuMoveUp( self, event ):
        # TODO menu handler
        logging.warning( "Move Up" )

    def OnMenuMoveDown( self, event ):
        # TODO menu handler
        logging.warning( "Move Down" )

    def OnMenuShowTimers( self, event ):
        # TODO menu handler
        logging.warning( "Show Timers" )

    def OnMenuShowAllCodes( self, event ):
        # TODO menu handler
        logging.warning( "Show All Codes" )

    def OnMenuHelpContents( self, event ):
        # TODO menu handler
        logging.warning( "Help Contents" )

    def OnMenuAbout( self, event ):
        # TODO menu handler
        logging.warning( "About" )


    def CalcItemsShown( self ):
        ws = self.GetClientSize()
        # Doing integer math, so we can't cancel terms and add 1/2
        n = ws.GetHeight() + ( self.entry_size.GetHeight() + 2 * self.entry_border ) / 2
        d = self.entry_size.GetHeight() + 2 * self.entry_border
        return n / d


    def AdjustWindowSizes( self ):
        logging.debug( "AF  AWS size:  %s", str( self.entry_size ) )
        # Need to adjust this here, it depends on the entry height which may change
        self.entries_window.SetScrollRate( 0, self.entry_size.GetHeight() + 2 * self.entry_border )

        # Frame size is 1 entry wide accounting for scrollbar, visible_entries high
        client_size = wx.DefaultSize
        client_size.SetWidth( self.entry_size.GetWidth() + 2 * self.entry_border + self.scrollbar_width )
        client_size.SetHeight( self.visible_entries * ( self.entry_size.GetHeight() + 2 * self.entry_border ) )
        self.entries_window.SetClientSize( client_size )

        # Minimum size is 1 entry wide accounting for scrollbar, 1 entry high
        min_size = wx.DefaultSize
        min_size.SetWidth( self.entry_size.GetWidth() + 2 * self.entry_border + self.scrollbar_width )
        min_size.SetHeight( self.entry_size.GetHeight() + 2 * self.entry_border )
        self.entries_window.SetMinClientSize( min_size )

        self.entries_window.GetSizer().Fit( self )
        logging.debug( "AF  AWS items: %d", self.CalcItemsShown() )


    def AdjustPanelSizes( self ):
        logging.debug( "AF  APS" )
        self.entry_size = wx.DefaultSize
        self.label_width = 0
        for entry in self.entry_panels:
            logging.debug( "AF  APS checking %s", entry.GetName() )
            # Update max entry panel sizes
            entry_size = entry.GetPanelSize()
            if entry_size.GetHeight() > self.entry_size.GetHeight():
                self.entry_size.SetHeight( entry_size.GetHeight() )
            if entry_size.GetWidth() > self.entry_size.GetWidth():
                self.entry_size.SetWidth( entry_size.GetWidth() )
            label_width = entry.GetLabelWidth()
            if label_width > self.label_width:
                self.label_width = label_width
            logging.debug( "AF  APS entry %s: %s label %d", entry.GetName(),
                           str( self.entry_size ), self.label_width )
        for entry in self.entry_panels:
            entry.ResizePanel( self.entry_size, self.label_width )
        self.entries_window.GetSizer().Fit( self.entries_window )
                

    def UpdatePanelSize( self ):
        self.AdjustPanelSizes()
        self.AdjustWindowSizes()
        self.Refresh()
