# -*- coding: utf-8 -*-

import wx
# TODO configuration
import AuthEntrySizer

class AuthFrame( wx.Frame ):

    def __init__( self ):
        wx.Frame.__init__( self, parent=None, id=wx.ID_ANY, title=_("PyAuth") )

        # TODO hook up window close event

        # Create and populate main menu bar, add to frame
        menu_bar = create_menubar()
        self.SetMenuBar( menu_bar )

        # Create auth codes container, populate with entries or dummy entry
        auth_container = wx.BoxSizer( wx.VERTICAL )
        entries = populate_container( auth_container )

        auth_window = wx.ScrolledWindow( self )
        # TODO Add container to window
        
        # TODO Set frame size based on number of entries and max number to be shown
        # TODO Fit container properly
        # TODO Set scrollbars properly


    def create_menubar():
        # TODO create_menubar
        return menu_bar


    def populate_container( container ):
        # TODO populate_container
        return entry_count
