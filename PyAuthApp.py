# -*- coding: utf-8 -*-

# .PyAuth - configuration directory
#     config - configuration
#     database.xml - authorization secrets storage

import PyAuth_xrc
import wx
from wx import xrc

class PyAuthApp(wx.App):

    def OnInit(self):
        # TODO Load data from storage file

        self.res = get_resources();
        init_frame(self)
        return True

    def init_frame(self)
        self.frame = self.res.LoadFrame(None, 'main_frame')
        # TODO get needed items
        # TODO do other needed initialization
        self.frame.Show()
