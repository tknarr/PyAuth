#!/usr/bin/python
# -*- coding: utf-8 -*-

# ${HOME}/.PyAuth/ - configuration directory
#     config - configuration
#     database.xml - authorization secrets storage

import sys
import wx
from wx import xrc
import AuthFrame

class PyAuthApp( wx.App ):

    def OnInit( self ):
        # TODO Init singleton authorization secrets storage

        # Load XRC resources
        self.xrc_path = sys.path[0] + "/xrc/"
        self.res = xrc.XmlResource( self.xrc_path + "auth_window.xrc" )

        self.frame = self.res.LoadFrame( None, 'main_frame' )
        self.SetTopWindow( self.frame )
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
