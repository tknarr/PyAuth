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

        self.provider_literal = "Provider:"
        self.account_literal = "Account:"
        self.secret_literal = "Secret:"
        self.original_label_literal = "Original label:"
        self.required_literal = "(required)"

        self.text_color = self.GetForegroundColour()

        vbox = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( vbox )

        vbox.AddSpacer( 16, 0 )

        # Item 1
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.provider_literal, True )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.provider_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.provider_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 2
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.account_literal, True )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.account_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.account_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 3
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.secret_literal, True )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.secret_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.secret_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 4
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.original_label_literal, False )
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
        err = False
        f = self.provider_text.IsEmpty()
        err = err or f
        self.ColorLabel( self.provider_label, f )
        f = self.account_text.IsEmpty()
        err = err or f
        self.ColorLabel( self.account_label, f )
        f = self.secret_text.IsEmpty()
        err = err or f
        self.ColorLabel( self.secret_label, f )
        if err:
            wx.Bell()
        else:
            event.Skip( True )

                
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

    def ColorLabel( self, ctrl, error ):
        if error:
            ctrl.SetForegroundColour( wx.RED )
        else:
            ctrl.SetForegroundColour( self.text_color )

    def MakeLabel( self, ctrl, txt, required ):
        lbl = txt
        if required:
            lbl += ' ' + self.required_literal
        ctrl.SetLabelText( lbl )
        ctrl.SetMinSize( wx.DLG_SZE( self, ctrl.GetTextExtent( ctrl.GetLabelText() ) ) )
