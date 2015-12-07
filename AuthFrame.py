# -*- coding: utf-8 -*-

import wx
# TODO configuration

class AuthFrame( wx.Frame ):

    def __init__( self ):
        wx.Frame.__init__( self, parent = None, id = wx.ID_ANY, title = "PyAuth" )

        # TODO hook up window close event

        # Create and populate main menu bar, add to frame
        self.menu_bar = self.create_menubar()
        #self.SetMenuBar( menu_bar )

        self.auth_window = wx.ScrolledWindow( self )

        # Create auth codes container, populate with entries or dummy entry
        self.auth_container = wx.BoxSizer( wx.VERTICAL )
        self.entries = self.populate_container( self.auth_window, self.auth_container )
        self.auth_window.SetSizer( self.auth_container )
        
        # TODO Set frame size based on number of entries and max number to be shown
        # TODO Fit container properly
        # TODO Set scrollbars properly


    def create_menubar( self ):
        # TODO create_menubar
        #return menu_bar
        return None


    def populate_container( self, window, container ):
        # TODO Populate container for real

        # Populate container with dummy entry
        item_panel = wx.Panel( window, name = "item_panel_0" )
        item_container = wx.BoxSizer( wx.HORIZONTAL )
        item_panel.SetSizer( item_container )

        # TODO Correct fonts/sizes and use derived classes
        label_container = wx.BoxSizer( wx.VERTICAL )
        label_container.Add( wx.StaticText( item_panel, label = "PROVIDER", name = "provider_text" ) )
        label_container.Add( wx.StaticText( item_panel, label = "ACCOUNT", name = "account_text" ) )
        item_container.Add( label_container )
        item_container.Add( wx.StaticText( item_panel, label = "000000", name = "code_text" ) )
        item_container.Add( wx.Gauge( item_panel, range = 30, name = "timer_gauge" ) )

        #return entry_count
        return 1
