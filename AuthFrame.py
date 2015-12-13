# -*- coding: utf-8 -*-

import wx
import Configuration
import AuthenticationStore
from AuthenticationStore import AuthenticationStore

class AuthFrame( wx.Frame ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr ):
        wx.Frame.__init__( self, parent, id, title, pos, size, style, name )

        self.entry_window = None
        self.entry_panels = []
        self.current_entries = 0
        self.visible_entries = Configuration.GetNumberOfItemsShown()
        self.scrollbar_width = 0
        self.entry_height = 0     # Height of tallest entry panel
        self.entry_width = 0      # Width of widest entry panel
        self.label_width = 0      # Width of widest label panel in any entry panel

        # Internal values
        self.entry_border = 2

        self.auth_store = AuthenticationStore( Configuration.GetDatabasePath() )

        # Create children
        self.SetMenuBar( self.build_menus() )
        self.entry_window = wx.ScrolledWindow( self, wx.ID_ANY, style = wx.VSCROLL, name = "entry_window" )
        self.entry_window.SetSizer( wx.BoxSizer( wx.VERTICAL ) )

        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.entry_window )
        self.entry_panels = self.populate_container
        self.current_entries = len(self.entry_panels)
        self.AdjustWindowSizes()
        auth_container = self.entry_window.GetSizer()
        for item in self.entry_panels:
            item.AdjustSizes( self.entry_width, self.entry_height, self.label_width )
            flags = wx.SizerFlags().Border( wx.ALL, self.entry_border ).Left().CenterVertical()
            auth_container.Add( item, flags )

        # Event handlers
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        # TODO Menu event handlers

        # TODO Fit/Layout as needed
        

    def OnCloseWindow( self, event ):
        self.auth_store.Save()
        wp = self.GetPosition()
        Configuration.SetLastWindowPosition( wp )
        ws = self.GetClientSize()
        items = self.CalcItemsShown( ws )
        Configuration.SetNumberOfItemsShown( items )
        Configuration.Save()
        self.Destroy()


    def CalcItemsShown( self, ws ):
        # Doing integer math, so we can't cancel terms and add 1/2
        n = ws.GetHeight() + ( self.entry_height + 2 * self.entry_border ) / 2
        d = self.entry_height + 2 * self.entry_border
        return n / d


    def AdjustWindowSizes( self ):
        # Need to adjust this here, it depends on the entry height which may change
        self.entry_window.SetScrollRate( 0, self.entry_height + 2 * self.entry_border )

        # Frame size is 1 entry wide accounting for scrollbar, visible_entries high
        client_size = wx.Size()
        client_size.SetWidth( self.entry_width + 2 * self.entry_border + self.scrollbar_width )
        client_size.SetHeight( self.visible_entries * ( self.entry_height + 2 * self.entry_border ) )
        self.entry_window.SetSize( client_size )
        self.SetClientSize( client_size )

        # Minimum size is 1 entry wide accounting for scrollbar, 1 entry high
        min_size = wx.Size()
        min_size.SetWidth( self.entry_width + 2 * self.entry_border + self.scrollbar_width )
        min_size.SetHeight( self.entry_height + 2 * self.entry_border )
        self.entry_window.SetMinSize( min_size )
        self.SetMinClientSize( min_size )
        

    def populate_container( self ):
        # Populate container from authentication store
        l = []
        for entry in self.auth_store.EntryList():
            item = self.create_item( entry )

            # Update max entry panel sizes
            item_size = item.GetSize()
            if item_size.GetHeight() > self.entry_height:
                self.entry_height = item_size.GetHeight()
            if item_size.GetWidth() > self.entry_width:
                self.entry_width = item_size.GetWidth()
            if item.GetLabelWidth() > self.label_width:
                self.label_width = item.GetLabelWidth()

            l.append( item )

        return l


    def create_item( self, entry ):
        # TODO Create entry panel
        ## item = self.res.LoadPanel( self.entry_window, 'entry_panel' )
        item.SetEntry( entry )
        return item


    def build_menus( self ):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        view_menu = wx.Menu()
        help_menu = wx.Menu()
        
        # TODO Build menus

        menu_bar.Append( file_menu, "&File" )
        menu_bar.Append( edit_menu, "&Edit" )
        menu_bar.Append( view_menu, "&View" )
        menu_bar.Append( help_menu, "&Help" )

        return menu_bar
