# -*- coding: utf-8 -*-

import wx
# TODO configuration

class AuthFrame( wx.Frame ):

    def __init__( self ):
        wx.Frame.__init__( self, parent = None, id = wx.ID_ANY, title = "PyAuth" )

        # GUI elements
        self.auth_window = None    # Scrolled window for code entries
        self.auth_container = None # Vertical sizer containing code entries
        self.entries = 0           # Number of code entries total
        self.entry_height = 0      # Pixel height of one code entry
        self.entry_width = 0       # Pixel width of widest code entry
        
        # Item fonts
        self.font_provider = wx.Font( 12, wx.MODERN, wx.NORMAL, wx.BOLD )
        self.font_account = wx.Font( 12, wx.MODERN, wx.NORMAL, wx.NORMAL )
        self.font_code = wx.Font( 32, wx.MODERN, wx.NORMAL, wx.NORMAL )

        # TODO hook up window close event

        # Create and populate main menu bar, add to frame
        menu_bar = self.create_menubar()
        #self.SetMenuBar( menu_bar )

        # Create auth codes container, populate with entries or dummy entry
        self.auth_window = wx.ScrolledWindow( self )
        self.auth_container = wx.BoxSizer( wx.VERTICAL )
        self.auth_window.SetSizer( self.auth_container )
        self.entries = self.populate_container( self.auth_window, self.auth_container )
        self.auth_container.Fit( self.auth_window )

        self.SetClientSize( self.auth_window.GetSize() )
        # TODO Set scrollbars properly


    def create_menubar( self ):
        # TODO create_menubar
        #return menu_bar
        return None


    def populate_container( self, window, container ):
        # TODO Populate container for real

        # Populate container with dummy entry
        item_panel = wx.Panel( window, name = "item_panel_0", style = wx.SUNKEN_BORDER )
        item_container = wx.BoxSizer( wx.HORIZONTAL )
        item_panel.SetSizer( item_container )

        # TODO Use derived classes
        label_container = wx.BoxSizer( wx.VERTICAL )
        x = wx.StaticText( item_panel, label = "PROVIDER", name = "provider_text", style = wx.ALIGN_LEFT )
        x.SetFont( self.font_provider )
        label_container.Add( x, border = 1, flag = wx.TOP | wx.BOTTOM )
        x = wx.StaticText( item_panel, label = "ACCOUNT", name = "account_text", style = wx.ALIGN_LEFT )
        x.SetFont( self.font_account )
        label_container.Add( x, border = 1, flag = wx.TOP | wx.BOTTOM )
        item_container.Add( label_container, border = 5, flag = wx.LEFT | wx.RIGHT )
        x = wx.StaticText( item_panel, label = "000000", name = "code_text", style = wx.ALIGN_LEFT )
        x.SetFont( self.font_code )
        item_container.Add( x, border = 5, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL )
        x = wx.Gauge( item_panel, range = 30, size = (30,15), name = "timer_gauge" )
        item_container.Add( x, border = 5, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL )
        item_container.Fit( item_panel )

        container.Add( item_panel, border = 2, flag = wx.TOP | wx.BOTTOM )
        self.entry_height = item_panel.GetSize().GetHeight() + 4
        self.entry_width = item_panel.GetSize().GetWidth()

        container.Fit( window )
        #return entry_count
        return 1
