# -*- coding: utf-8 -*-

import wx
from Logging import GetLogger

class DatabasePasswordDialog( wx.Dialog ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_DIALOG_STYLE, name = wx.DialogNameStr ):
        wx.Dialog.__init__( self, parent, id, title, pos, size, style, name )

        GetLogger().debug( "PWD init" )

        # TODO

        vbox = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( vbox )

        vbox.AddSpacer( 16, 0 )

        # TODO

        vbox.AddSpacer( 16, 0 )

        vbox.AddStretchSpacer( 1 )

        btnsizer = self.CreateButtonSizer( wx.OK | wx.CANCEL )
        if btnsizer != None:
            vbox.Add( btnsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8 )

        self.GetSizer().Fit( self )

        self.Bind( wx.EVT_BUTTON, self.OnOK, id = wx.ID_OK )

        GetLogger().debug( "PWD init done" )


    def OnOK( self, event ):
        err = False
        # TODO
        if err:
            GetLogger().debug( "PWD OK button missing required items" )
            wx.Bell()
        else:
            GetLogger().debug( "PWD OK button" )
            event.Skip( True )


    def Reset( self ):
        GetLogger().debug( "PWD reset" )
        # TODO
