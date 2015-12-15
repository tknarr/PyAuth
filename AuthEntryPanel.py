# -*- coding: utf-8 -*-

import wx
from wx import xrc as xrc
from AuthenticationStore import AuthenticationEntry

class AuthEntryPanel( wx.Panel ):
    # TODO Convert to XRC

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr, auth_entry = None ):
        wx.Panel.__init__( self, parent, id, pos, size, style, name )
        self.SetSizer( wx.BoxSizer( wx.HORIZONTAL ) )
        font = wx.Font( 12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
        self.SetFont( font )

        if auth_entry != None:
            self.SetEntry( auth_entry )
        else:
            self.SetEntry( AuthenticationStore.AuthenticationEntry( 0, 0 ) )

        # Build child windows
        self.label_panel = wx.Panel( self, name = "label_panel" )
        self.label_panel.SetBackgroundColour( wx.GREEN )
        self.label_panel.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
        self.provider_ctrl = wx.StaticText( self.label_panel, wx.ID_ANY, self.entry.GetProvider(),
                                            name = "provider_ctrl" )
        self.account_ctrl = wx.StaticText( self.label_panel, wx.ID_ANY, self.entry.GetAccount(),
                                           name = "account_ctrl" )
        self.label_panel.GetSizer().Add( self.provider_ctrl )
        self.label_panel.GetSizer().Add( self.account_ctrl )

        self.code_panel = wx.Panel( self, name = "code_panel" )
        self.code_panel.SetBackgroundColour( wx.CYAN )
        font = wx.Font( 32, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
        self.code_panel.SetFont( font )
        self.code_panel.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
        self.code_ctrl = wx.StaticText( self.code_panel, wx.ID_ANY, " 000000 ",
                                        name = "code_ctrl",
                                        style = wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE )
        tx = self.code_ctrl.GetTextExtent( " 000000 " ) # Max-size code plus a bit of padding
        self.code_minsize = wx.Size( tx[0], tx[1] )
        self.code_ctrl.SetSize( self.code_minsize )
        self.code_ctrl.SetMinSize( self.code_minsize )
        self.code_panel.GetSizer().Add( self.code_ctrl, flag = wx.ALIGN_CENTER | wx.FIXED_MINSIZE )

        self.timer_panel = wx.Panel( self, name = "timer_panel" )
        self.timer_panel.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
        self.timer_ctrl = wx.Gauge( self.timer_panel, wx.ID_ANY, 30, name="timer_ctrl",
                                    style = wx.GA_HORIZONTAL )
        self.timer_ctrl.SetMinSize( self.timer_ctrl.GetSize() )
        self.timer_panel.GetSizer().Add( self.timer_ctrl, flag = wx.ALIGN_CENTER | wx.FIXED_MINSIZE  )

        self.label_panel_width = self.label_panel.GetSize().GetWidth()


    def GetEntry( self ):
        return self.entry

    def SetEntry( self, entry ):
        self.entry = entry
        self.SetName( "entry_panel_%s" % self.entry.GetGroup() )
        self.index = self.entry.GetSortIndex()
        self.code = entry.GenerateNextCode()


    def GetLabelPanelWidth( self ):
        return self.label_panel_width

    def SetLabelPanelWidth( self, label_panel_width ):
        self.label_panel_width = label_panel_width
        lpsize = self.label_panel.GetSize()
        lpsize.SetWidth( self.label_panel_width )
        self.label_panel.SetSize( lpsize )
        self.label_panel.SetMinSize( lpsize )


    def SetPanelSize( self, panel_size, label_panel_width = 0 ):
        if label_panel_width > 0:
            self.SetLabelPanelWidth( label_panel_width )
        self.SetSize( panel_size )
        self.SetMinSize( panel_size )


    def UpdateContents( self ):
        self.code_ctrl.SetLabelText( self.code )
        self.provider_ctrl.SetLabelText( self.entry.GetProvider() )
        self.account_ctrl.SetLabelText( self.entry.GetAccount() )
        self.provider_ctrl.SetMinSize( self.provider_ctrl.GetSize() )
        self.account_ctrl.SetMinSize( self.account_ctrl.GetSize() )
        psize = self.provider_ctrl.GetSize()
        new_width = psize.GetWidth()
        asize = self.account_ctrl.GetSize()
        if asize.GetWidth() > new_width:
            new_width = asize.GetWidth()
        self.SetLabelPanelWidth( new_width )
        gp = self.GetGrandParent()
        if gp != None:
            gp.UpdatePanelSize()
