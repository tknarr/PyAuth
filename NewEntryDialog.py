# -*- coding: utf-8 -*-

import logging
import wx

class NewEntryDialog( wx.Dialog ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  name = wx.DialogNameStr ):
        wx.Dialog.__init__( self, parent, id, title, pos, size,
                             wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name )

        self.provider_label = None
        self.provider_text = None
        self.account_label = None
        self.account_text = None
        self.secret_label = None
        self.secret_text = None
        self.original_label_label = None
        self.original_label_text = None

        vbox = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( vbox )

        vbox.AddSpacer( 16, 0 )

        # Item 1
        lbl = wx.StaticText( self, wx.ID_ANY, "Provider:" )
        lbl.SetMinSize( wx.DLG_SZE( self, lbl.GetTextExtent( lbl.GetLabelText() ) ) )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.provider_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.provider_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 2
        lbl = wx.StaticText( self, wx.ID_ANY, "Account:" )
        lbl.SetMinSize( wx.DLG_SZE( self, lbl.GetTextExtent( lbl.GetLabelText() ) ) )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.account_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.account_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 3
        lbl = wx.StaticText( self, wx.ID_ANY, "Secret:" )
        lbl.SetMinSize( wx.DLG_SZE( self, lbl.GetTextExtent( lbl.GetLabelText() ) ) )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.secret_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.secret_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 4
        lbl = wx.StaticText( self, wx.ID_ANY, "Original label:" )
        lbl.SetMinSize( wx.DLG_SZE( self, lbl.GetTextExtent( lbl.GetLabelText() ) ) )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.original_label_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.original_label_text = txt

        vbox.AddSpacer( 16, 0 )

        vbox.AddStretchSpacer( 1 )

        btnsizer = self.CreateButtonSizer( wx.OK | wx.CANCEL )
        vbox.Add( btnsizer, 0, wx.ALL, 8 )

        self.GetSizer().Fit( self )

        self.Bind( wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK )


    def OnOK( self, event ):
        # TODO validation and error message
        self.Close()


    def GetProviderValue( self ):
        return self.provider_text.GetValue()

    def GetAccountValue( self ):
        return self.account_text.GetValue()

    def GetSecretValue( self ):
        return self.secret_text.GetValue()

    def GetOriginalLabel( self ):
        return self.original_label_text.GetValue()

    def Reset( self ):
        self.provider_text.Clear()
        self.account_text.Clear()
        self.secret_text.Clear()
        self.original_label_text.Clear()
