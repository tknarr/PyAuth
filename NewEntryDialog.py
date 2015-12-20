# -*- coding: utf-8 -*-

import logging
import wx

class NewEntryDialog( wx.Dialog ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  name = wx.DialogNameStr ):
        wx.Dialog.__init__( self, parent, id, title, pos, size,
                             wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name )

        self.provider_text = None
        self.account_text = None
        self.secret_text = None
        self.original_label_text = None
        self.error_message = None

        vbox = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( vbox )

        fgs = wx.FlexGridSizer( 4, 2 )
        fgs.SetFlexibleDirection( wx.HORIZONTAL )
        fgs.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
        fgs.AddGrowableCol( 1, 1 )
        vbox.Add( fgs, 0, wx.ALL, 16 )

        # Row 1
        lbl = wx.StaticText( self, wx.ID_ANY, "Provider:" )
        lbl.SetMinSize( self.GetTextExtent( "Provider:" ) )
        fgs.Add( lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0 )
        self.provider_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        self.provider_text.SetMinSize( self.provider_text.GetTextExtent( 'MMMMMMMMMM' ) )
        fgs.Add( self.provider_text, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )

        # Row 2
        lbl = wx.StaticText( self, wx.ID_ANY, "Account:" )
        lbl.SetMinSize( self.GetTextExtent( "Account:" ) )
        fgs.Add( lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0 )
        self.account_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        fgs.Add( self.account_text, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )

        # Row 3
        lbl = wx.StaticText( self, wx.ID_ANY, "Secret:", )
        lbl.SetMinSize( self.GetTextExtent( "Secret:" ) )
        fgs.Add( lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0 )
        self.secret_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        fgs.Add( self.secret_text, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )

        # Row 4
        lbl = wx.StaticText( self, wx.ID_ANY, "Original label:" )
        lbl.SetMinSize( self.GetTextExtent( "Original Label:" ) )
        fgs.Add( lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0 )
        self.original_label_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        fgs.Add( self.original_label_text, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0 )

        self.error_message = wx.StaticText( self, wx.ID_ANY, '' )
        self.error_message.SetMinSize( self.error_message.GetTextExtent( 'M' ) )
        vbox.Add( self.error_message, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 16 )

        vbox.AddStretchSpacer( 1 )

        btnsizer = self.CreateButtonSizer( wx.OK | wx.CANCEL )
        vbox.Add( btnsizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 16 )

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

    def SetErrorMessage( self, msg ):
        self.error_message.SetLabel( msg )
        if msg != '':
            self.error_message.SetMinSize( self.error_message.GetTextExtent( msg ) )
        else:
            self.error_message.SetMinSize( self.error_message.GetTextExtent( 'M' ) )

    def Reset( self ):
        self.provider_text.Clear()
        self.account_text.Clear()
        self.secret_text.Clear()
        self.original_label_text.Clear()
        self.SetErrorMessage( '' )
