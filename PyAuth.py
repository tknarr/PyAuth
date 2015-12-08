#!/usr/bin/python
# -*- coding: utf-8 -*-

# ${HOME}/.PyAuth/ - configuration directory
#     config - configuration
#     database.xml - authorization secrets storage

import sys
import wx
from wx import xrc
from AuthFrame import AuthFrame

class PyAuthApp( wx.App ):

    def OnInit( self ):
        # TODO Init singleton authorization secrets storage

        # Load XRC resources
        self.xrc_path = sys.path[0] + "/xrc/"
        self.xrc_res = xrc.XmlResource( self.xrc_path + "auth_window.xrc" )

        self.frame = self.xrc_res.LoadFrame( None, 'main_frame' )
        self.SetTopWindow( self.frame )
        self.frame.Show()
        return True

    def res():
        # Make XRC resources available to other components
        return self.xrc_res


if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
