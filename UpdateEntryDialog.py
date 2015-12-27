# -*- coding: utf-8 -*-

import logging
import wx

class UpdateEntryDialog( wx.Dialog ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_DIALOG_STYLE, name = wx.DialogNameStr ):
        wx.Dialog.__init__( self, parent, id, title, pos, size, style, name )

        logging.debug( "UED init" )
        
        self.provider_label = None
        self.provider_text = None
        self.account_label = None
        self.account_text = None
        self.secret_label = None
        self.secret_text = None

        self.provider_literal = "Provider:"
        self.account_literal = "Account:"
        self.secret_literal = "Secret:"
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
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMMMMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.provider_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 2
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.account_literal, True )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.account_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMMMMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.account_text = txt

        vbox.AddSpacer( 16, 0 )

        # Item 3
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.secret_literal, True )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.secret_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        txt.SetMinSize( wx.DLG_SZE( self, txt.GetTextExtent( 'MMMMMMMMMMMMMMMMMMMM' ) ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.secret_text = txt

        vbox.AddSpacer( 16, 0 )

        vbox.AddStretchSpacer( 1 )

        btnsizer = self.CreateButtonSizer( wx.OK | wx.CANCEL )
        if btnSizer != None:
            vbox.Add( btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8 )

        self.GetSizer().Fit( self )

        self.Bind( wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK )

        logging.debug( "UED init done" )


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
            logging.debug( "UED OK button missing required items" )
            wx.Bell()
        else:
            logging.debug( "UED OK button" )
            event.Skip( True )

                
    def GetProviderValue( self ):
        return self.provider_text.GetValue()

    def GetAccountValue( self ):
        return self.account_text.GetValue()

    def GetSecretValue( self ):
        return self.secret_text.GetValue()

    def Reset( self, provider, account, secret ):
        logging.debug( "UED reset" )
        self.provider_text.SetValue( provider )
        self.ColorLabel( self.provider_label, self.provider_text.IsEmpty() )
        self.account_text.SetValue( account )
        self.ColorLabel( self.account_label, self.account_text.IsEmpty() )
        self.secret_text.SetValue( secret )
        self.ColorLabel( self.secret_label, self.secret_text.IsEmpty() )

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
