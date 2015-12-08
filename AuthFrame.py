# -*- coding: utf-8 -*-

import wx
# TODO configuration

class AuthFrame( wx.Frame ):

    def __init__( self ):
        wx.Frame.__init__( self, parent = None, id = wx.ID_ANY, title = "PyAuth" )

        self.res = wx.GetApp().res()

        # Locate and save references to important GUI elements
        self.auth_window = self.XRCCTRL( self, 'codes_window' )
        self.auth_container = self.XRCCTRL( self.auth_window, 'codes_sizer' )
        self.entries = populate_container()

        self.SetClientSize( self.auth_window.GetSize() )
        # TODO Set scrollbars properly

    def populate_container( self ):
        # TODO Populate container for real

        # Populate container with dummy entry
        item = self.res.LoadPanel( self.auth_window, 'entry_panel' )
        item.SetName( 'entry_0' )

        # MARK

        # TODO Use derived classes
        ## label_container = wx.BoxSizer( wx.VERTICAL )
        ## x = wx.StaticText( item_panel, label = "PROVIDER", name = "provider_text", style = wx.ALIGN_LEFT )
        ## x.SetFont( self.font_provider )
        ## label_container.Add( x, border = 1, flag = wx.TOP | wx.BOTTOM )
        ## x = wx.StaticText( item_panel, label = "ACCOUNT", name = "account_text", style = wx.ALIGN_LEFT )
        ## x.SetFont( self.font_account )
        ## label_container.Add( x, border = 1, flag = wx.TOP | wx.BOTTOM )
        ## item_container.Add( label_container, border = 5, flag = wx.LEFT | wx.RIGHT )
        ## x = wx.StaticText( item_panel, label = "000000", name = "code_text", style = wx.ALIGN_LEFT )
        ## x.SetFont( self.font_code )
        ## item_container.Add( x, border = 5, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL )
        ## x = wx.Gauge( item_panel, range = 30, size = (30,15), name = "timer_gauge" )
        ## item_container.Add( x, border = 5, flag = wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL )
        ## item_container.Fit( item_panel )

        ## container.Add( item_panel, border = 2, flag = wx.TOP | wx.BOTTOM )
        ## self.entry_height = item_panel.GetSize().GetHeight() + 4
        ## self.entry_width = item_panel.GetSize().GetWidth()

        #return entry_count
        return 1
