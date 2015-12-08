# -*- coding: utf-8 -*-

import wx
from wx import xrc
# TODO configuration

class AuthFrame( wx.Frame ):

    def __init__( self ):
        wx.Frame.__init__( self, parent = None, id = wx.ID_ANY, title = "PyAuth" )

        self.res = wx.GetApp().res

        # Locate and save references to important GUI elements
        self.auth_window = xrc.XRCCTRL( self, 'codes_window' )
        self.auth_container = xrc.XRCCTRL( self, 'codes_sizer' )
        self.entries = self.populate_container()

        self.SetClientSize( self.auth_window.GetSize() )
        # TODO Set scrollbars properly

    def populate_container( self ):
        # TODO Populate container for real

        # Populate container with dummy entry
        item = self.res.LoadPanel( self.auth_window, 'entry_panel' )
        item.SetName( 'entry_0' )
        # Set minimum size correctly
        s = item.GetSize()
        s.IncBy( 0, 4 )
        item.SetSize( s )
        f = wx.SizerFlags().Align( wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL ).Border( wx.ALL, 2 )
        self.auth_container.Add( item, f )

        #return entry_count
        return 1
