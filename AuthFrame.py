# -*- coding: utf-8 -*-

import wx
import Configuration
from AuthenticationStore import AuthenticationStore, AuthenticationEntry
from AuthEntryPanel import AuthEntryPanel

class AuthFrame( wx.Frame ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr ):
        wx.Frame.__init__( self, parent, id, title, pos, size, style, name )

        self.ID_SHOW_TIMERS = self.NewControlId()
        self.ID_SHOW_ALL_CODES = self.NewControlId()
        
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

        self.auth_store = AuthenticationStore( Configuration.GetDatabaseFilename() )

        # Create child windows
        self.SetMenuBar( self.build_menus() )
        self.entry_window = wx.ScrolledWindow( self, wx.ID_ANY, style = wx.VSCROLL, name = "entry_window" )
        self.entry_window.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
        # Get scrollbar width so we can account for it in window sizing
        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.entry_window )

        # Create our entry item panels and put them in the scrollable window
        # Remember to adjust our own window sizes to match what's needed to fit the largest entry
        self.entry_panels = []
        for entry in self.auth_store.EntryList():
            item = self.create_panel( entry )
            self.entry_panels.append( item )
        self.current_entries = len( self.entry_panels )
        auth_container = self.entry_window.GetSizer()
        for item in self.entry_panels:
            auth_container.Add( item, flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 2 )
        self.AdjustPanelSizes() # This will call AdjustWindowSizes() for us

        # Window event handlers
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        # Menu event handlers
        wx.EVT_MENU( self, wx.ID_NEW, self.OnMenuNewEntry )
        wx.EVT_MENU( self, wx.ID_EXIT, self.OnMenuQuit )
        wx.EVT_MENU( self, wx.ID_EDIT, self.OnMenuEditEntry )
        wx.EVT_MENU( self, wx.ID_DELETE, self.OnMenuDeleteEntry )
        wx.EVT_MENU( self, wx.ID_UP, self.OnMenuMoveUp )
        wx.EVT_MENU( self, wx.ID_DOWN, self.OnMenuMoveDown )
        wx.EVT_MENU( self, self.ID_SHOW_TIMERS, self.OnMenuShowTimers )
        wx.EVT_MENU( self, self.ID_SHOW_ALL_CODES, self.OnMenuShowAllCodes )
        wx.EVT_MENU( self, wx.ID_HELP, self.OnMenuHelpContents )
        wx.EVT_MENU( self, wx.ID_ABOUT, self.OnMenuAbout )

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


    def AdjustPanelSizes( self ):
        self.entry_width = 0
        self.entry_height = 0
        for entry in self.entry_panels:
            # Update max entry panel sizes
            entry_size = entry.GetSize()
            if entry_size.GetHeight() > self.entry_height:
                self.entry_height = entry_size.GetHeight()
            if entry_size.GetWidth() > self.entry_width:
                self.entry_width = entry_size.GetWidth()
            if entry.GetLabelPanelWidth() > self.label_width:
                self.label_width = entry.GetLabelPanelWidth()
        ps = wx.Size( self.entry_width, self.entry_height )
        for entry in self.entry_panels:
            entry.SetPanelSize( ps, self.label_width )
        self.AdjustWindowSizes()
                

    def UpdatePanelSize( self ):
        self.AdjustPanelSizes()
        self.SendSizeEvent()
        

    def create_panel( self, entry ):
        # Create entry panel
        panel = AuthEntryPanel( self, wx.ID_ANY, auth_entry = entry )
        return panel


    def build_menus( self ):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        edit_menu = wx.Menu()
        view_menu = wx.Menu()
        help_menu = wx.Menu()

        # File menu
        file_menu.Append( wx.ID_NEW, "&New", "Create a new authentication entry" )
        file_menu.Append( wx.ID_EXIT, "&Quit", "Exit the program" )

        # Edit menu
        edit_menu.Append( wx.ID_EDIT, "&Edit", "Edit the selected authentication entry" )
        edit_menu.Append( wx.ID_DELETE, "Delete", "Delete the selected authentication entry" )
        edit_menu.AppendSeparator()
        edit_menu.Append( wx.ID_UP, "&Up", "Move selected authentication entry up one position" )
        edit_menu.Append( wx.ID_DOWN, "&Down", "Move selected authentication entry down one position" )

        # View menu
        timers = wx.MenuItem( view_menu, self.ID_SHOW_TIMERS, "Show &Timers", "Show timers",
                              kind = wx.ITEM_CHECK )
        ## timers.Check( True )
        view_menu.AppendItem( timers )
        all_codes = wx.MenuItem( view_menu, self.ID_SHOW_ALL_CODES, "Show All &Codes",
                                 "Show codes for all entries",
                                 kind = wx.ITEM_CHECK )
        ## all_codes.Check( True )
        view_menu.AppendItem( all_codes )
        
        # Help menu
        help_menu.Append( wx.ID_HELP, "&Help contents", "Help contents" )
        help_menu.Append( wx.ID_ABOUT, "About", "About PyAuth" )

        menu_bar.Append( file_menu, "&File" )
        menu_bar.Append( edit_menu, "&Edit" )
        menu_bar.Append( view_menu, "&View" )
        menu_bar.Append( help_menu, "&Help" )

        return menu_bar
