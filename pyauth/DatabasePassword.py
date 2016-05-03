# -*- coding: utf-8 -*-
"""Database password dialog box."""

import wx
from Logging import GetLogger

class DatabasePasswordDialog( wx.Dialog ):
    """Database password dialog box."""

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_DIALOG_STYLE, name = wx.DialogNameStr ):
        """Initialize the dialog box."""
        wx.Dialog.__init__( self, parent, id, title, pos, size, style, name )

        GetLogger().debug( "PWD init" )

        self.password_label = None
        self.password_text = None

        self.password_literal = "Password:"

        vbox = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( vbox )

        vbox.AddSpacer( 16, 0 )

        # Password
        lbl = wx.StaticText( self, wx.ID_ANY, '' )
        self.MakeLabel( lbl, self.password_literal, True )
        vbox.Add( lbl, 0, wx.LEFT | wx.RIGHT, 8 )
        self.password_label = lbl
        txt = wx.TextCtrl( self, wx.ID_ANY, '', style = wx.TE_LEFT | wx.TE_DONTWRAP )
        te = txt.GetTextExtent( 'M' * 20 )
        txt.SetMinClientSize( wx.DLG_SZE( self, te ) )
        vbox.Add( txt, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 8 )
        self.password_text = txt

        vbox.AddSpacer( 16, 0 )

        vbox.AddStretchSpacer( 1 )

        btnsizer = self.CreateButtonSizer( wx.OK | wx.CANCEL )
        if btnsizer != None:
            vbox.Add( btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8 )

        self.GetSizer().Fit( self )

        self.Bind( wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK )

        GetLogger().debug( "PWD init done" )


    def OnOK( self, event ):
        """Handle the OK button event."""
        GetLogger().debug( "PWD OK button" )
        event.Skip( True )


    def GetPasswordValue( self ):
        """Return the contents of the password field."""
        return self.password_text.GetValue()


    def Reset( self ):
        """Reset the dialog box contents."""
        GetLogger().debug( "PWD reset" )
        self.password_text.Clear()


    def MakeLabel( self, ctrl, txt, required ):
        """Set up a label control's text."""
        ctrl.SetLabelText( txt )
        ctrl.SetMinSize( wx.DLG_SZE( self, ctrl.GetTextExtent( ctrl.GetLabelText() ) ) )
