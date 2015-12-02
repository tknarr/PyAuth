# -*- coding: utf-8 -*-

# .PyAuth - configuration directory
#     auth.xml - authorization file

class PyAuthApp(wx.App):

    def OnInt(self):
        # TODO Load data from storage file

        self.res = get_resources();
        # TODO Load and init main frame

        return True
