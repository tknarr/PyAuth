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
        vbox.Add( fgs, 0, wx.ALL, 8 )

        label_minsize = wx.Size( 0, 0 )
        labels = []
        
        # Row 1
        lbl = wx.StaticText( self, wx.ID_ANY, "Provider:", style = wx.ALIGN_RIGHT )
        lbl_te = lbl.GetTextExtent( lbl.GetLabelText() )
        if lbl_te[0] > label_minsize.GetWidth():
            label_minsize.SetWidth( lbl_te[0] )
        if lbl_te[1] > label_minsize.GetHeight():
            label_minsize.SetHeight( lbl_te[1] )
        labels.append( lbl )
        fgs.Add( lbl, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 2 )
        self.provider_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        self.provider_text.SetMinSize( wx.DLG_SZE( self, self.provider_text.GetTextExtent( 'MMMMMMMMMM' ) ) )
        fgs.Add( self.provider_text, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 2 )

        # Row 2
        lbl = wx.StaticText( self, wx.ID_ANY, "Account:", style = wx.ALIGN_RIGHT )
        lbl_te = lbl.GetTextExtent( lbl.GetLabelText() )
        if lbl_te[0] > label_minsize.GetWidth():
            label_minsize.SetWidth( lbl_te[0] )
        if lbl_te[1] > label_minsize.GetHeight():
            label_minsize.SetHeight( lbl_te[1] )
        labels.append( lbl )
        fgs.Add( lbl, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 2 )
        self.account_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        self.account_text.SetMinSize( wx.DLG_SZE( self, self.account_text.GetTextExtent( 'MMMMMMMMMM' ) ) )
        fgs.Add( self.account_text, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 2 )

        # Row 3
        lbl = wx.StaticText( self, wx.ID_ANY, "Secret:", style = wx.ALIGN_RIGHT )
        lbl_te = lbl.GetTextExtent( lbl.GetLabelText() )
        if lbl_te[0] > label_minsize.GetWidth():
            label_minsize.SetWidth( lbl_te[0] )
        if lbl_te[1] > label_minsize.GetHeight():
            label_minsize.SetHeight( lbl_te[1] )
        labels.append( lbl )
        fgs.Add( lbl, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 2 )
        self.secret_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        self.secret_text.SetMinSize( wx.DLG_SZE( self, self.secret_text.GetTextExtent( 'MMMMMMMMMM' ) ) )
        fgs.Add( self.secret_text, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 2 )

        # Row 4
        lbl = wx.StaticText( self, wx.ID_ANY, "Original label:", style = wx.ALIGN_RIGHT )
        lbl_te = lbl.GetTextExtent( lbl.GetLabelText() )
        if lbl_te[0] > label_minsize.GetWidth():
            label_minsize.SetWidth( lbl_te[0] )
        if lbl_te[1] > label_minsize.GetHeight():
            label_minsize.SetHeight( lbl_te[1] )
        labels.append( lbl )
        fgs.Add( lbl, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 2 )
        self.original_label_text = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        self.original_label_text.SetMinSize( wx.DLG_SZE( self, self.original_label_text.GetTextExtent( 'MMMMMMMMMM' ) ) )
        fgs.Add( self.original_label_text, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 2 )

        label_minsize_dlg = wx.DLG_SZE( self, label_minsize )
        for lbl in labels:
            lbl.SetSize( label_minsize_dlg )
            lbl.SetMinSize( label_minsize_dlg )

        self.error_message = wx.StaticText( self, wx.ID_ANY, '' )
        self.error_message.SetMinSize( wx.DLG_SZE( self, self.error_message.GetTextExtent( 'M' ) ) )
        vbox.Add( self.error_message, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 16 )

        vbox.AddStretchSpacer( 1 )

        btnsizer = self.CreateButtonSizer( wx.OK | wx.CANCEL )
        vbox.Add( btnsizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8 )

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
            self.error_message.SetMinSize( wx.DLG_SZE( self, self.error_message.GetTextExtent( msg ) ) )
        else:
            self.error_message.SetMinSize( wx.DLG_SZE( self, self.error_message.GetTextExtent( 'M' ) ) )

    def Reset( self ):
        self.provider_text.Clear()
        self.account_text.Clear()
        self.secret_text.Clear()
        self.original_label_text.Clear()
        self.SetErrorMessage( '' )
