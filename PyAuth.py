#!/usr/bin/python
# -*- coding: utf-8 -*-

# ${HOME}/.PyAuth/ - configuration directory
#     config - configuration
#     database.xml - authorization secrets storage

import wx
from AuthFrame import AuthFrame

class PyAuthApp( wx.App ):

    
    def OnInit( self ):
        # TODO Init singleton authorization secrets storage
        frame = AuthFrame()
        self.SetTopWindow( frame )
        frame.Show()
        return True


if __name__ == '__main__':
    app = PyAuthApp( False )
    app.MainLoop()
