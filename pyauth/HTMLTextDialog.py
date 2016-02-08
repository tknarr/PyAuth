# -*- coding: utf-8 -*-

import wx
import wx.html
from .Logging import GetLogger

class ClickableHTMLWindow( wx.html.HtmlWindow ):

    def __init__( self, parent, id = wx.ID_ANY, size = wx.DefaultSize ):
        wx.html.HtmlWindow.__init__( self, parent, id, size = size )
        if 'gtk2' in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked( self, link ):
        wx.LaunchDefaultBrowser( link.GetHref() )


class HTMLTextDialog( wx.Dialog ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME | wx.RESIZE_BORDER,
                  name = wx.DialogNameStr ):
        wx.Dialog.__init__( self, parent, id, title, pos, size, style, name )

        GetLogger().debug( "HTML text dialog init" )

        self.browser = None

        vbox = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( vbox )

        vbox.AddSpacer( 16, 0 )

        html = ClickableHTMLWindow( self, wx.ID_ANY, size = wx.Size( 600, 600 ) )
        self.browser = html
        vbox.Add( html, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        
        vbox.AddSpacer( 16, 0 )

        btnsizer = self.CreateButtonSizer( wx.OK )
        if btnsizer != None:
            vbox.Add( btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8 )

        self.GetSizer().Fit( self )

        self.Bind( wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK )

        GetLogger().debug( "HTML text dialog init done" )


    def LoadFile( self, fn ):
        if self.browser != None:
            self.browser.LoadFile( fn )


    def OnOK( self, event ):
        event.Skip( True )
