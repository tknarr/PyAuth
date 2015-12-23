# -*- coding: utf-8 -*-

import logging
import wx
from AuthenticationStore import AuthenticationEntry

class AuthEntryPanel( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr, entry = None ):
        wx.Panel.__init__ ( self, parent, id, pos, size, style, name )
        logging.debug( "AEP init" )

        self.entry = entry
        self.index = 0
        self.code = ''
        self.label_width = 0

        self.provider_text = None
        self.account_text = None
        self.code_text = None
        self.timer_gauge = None

        # Create panel child controls

        self.provider_font = wx.Font( 10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
        self.account_font = wx.Font( 10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
        self.code_font = wx.Font( 28, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

        sizer = wx.BoxSizer( wx.HORIZONTAL )
        self.SetSizer( sizer )

        label_sizer = wx.BoxSizer( wx.VERTICAL )

        self.provider_text = wx.StaticText( self, wx.ID_ANY, "PROVIDER", style = wx.ALIGN_LEFT,
                                            name = 'provider_text' )
        self.provider_text.Wrap( -1 )
        self.provider_text.SetFont( self.provider_font )
        label_sizer.Add( self.provider_text, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0 )

        self.account_text = wx.StaticText( self, wx.ID_ANY, "ACCOUNT", style = wx.ALIGN_LEFT,
                                           name = 'account_text' )
        self.account_text.Wrap( -1 )
        self.account_text.SetFont( self.account_font )
        label_sizer.Add( self.account_text, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0 )

        sizer.Add( label_sizer, 1, wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 2 )
        
        self.code_text = wx.StaticText( self, wx.ID_ANY, '000000', style = wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE,
                                        name = 'code_text' )
        self.code_text.Wrap( -1 )
        self.code_text.SetFont( self.code_font )
        sizer.Add( self.code_text, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER | wx.FIXED_MINSIZE, 12 )

        self.timer_gauge = wx.Gauge( self, wx.ID_ANY, 30, size = wx.Size( 30, 15 ),
                                     style = wx.GA_HORIZONTAL, name='timer_gauge' )
        self.timer_gauge.SetValue( 30 )
        sizer.Add( self.timer_gauge, 0, wx.RIGHT | wx.ALIGN_CENTER, 2 )

        # Initialize and size controls

        self.provider_text.SetMinSize( self.provider_text.GetSize() )
        self.account_text.SetMinSize( self.account_text.GetSize() )
        
        te = self.code_text.GetTextExtent( '000000' )
        self.code_text.SetClientSize( te )
        self.code_text.SetMinClientSize( te )

        self.timer_gauge.SetMinSize( self.timer_gauge.GetSize() )

        if entry != None:
            self.SetName( 'entry_panel_%s' % self.entry.GetGroup() )
            self.code = self.entry.GenerateNextCode()
        self.UpdateContents()

        self.Bind( wx.EVT_WINDOW_CREATE, self.OnCreate )

        logging.debug( "AEP init done" )


    def OnCreate( self, event ):
        self.Unbind( wx.EVT_WINDOW_CREATE )
        logging.debug( "AEP created" )
        self.Refresh()


    def GetEntry( self ):
        return self.entry

    def SetEntry( self, entry ):
        self.entry = entry
        self.SetName( 'entry_panel_%s' % self.entry.GetGroup() )
        self.index = self.entry.GetSortIndex()
        self.code = self.entry.GenerateNextCode()
        logging.debug( "AEP SE on %s", self.GetName() )
        self.ChangeContents()


    def GetPanelSize( self ):
        return self.GetSize()

    def GetLabelWidth( self ):
        return self.label_width


    def ResizePanel( self, panel_width, panel_height, label_width ):
        logging.debug( "AEP RP updating %s", self.GetName() )
        logging.debug( "AEP RP initial panel %s", str( self.GetSize() ) )
        logging.debug( "AEP RP initial label width %d", self.label_width )
        changed = False

        if label_width != self.label_width:
            logging.debug( "AEP RP label width: %d", label_width )
            self.label_width = label_width
            s = self.provider_text.GetClientSize()
            s.SetWidth( self.label_width )
            self.provider_text.SetClientSize( s )
            self.provider_text.SetMinClientSize( s )
            s = self.account_text.GetClientSize()
            s.SetWidth( self.label_width )
            self.account_text.SetClientSize( s )
            self.account_text.SetMinClientSize( s )
            changed = True

        if panel_height != self.GetSize().GetHeight() or panel_width != self.GetSize().GetWidth():
            logging.debug( "AEP RP panel size: %dx%d", panel_width, panel_height )
            s = wx.Size( panel_width, panel_height )
            self.SetSize( s )
            self.SetMinSize( s )
            changed = True

        logging.debug( "AEP RP label width: %d", self.label_width )
        logging.debug( "AEP RP panel size: %s", str( self.GetSize() ) )


    def UpdateContents( self ):
        if self.entry != None:
            logging.debug( "AEP UC updating %s", self.GetName() )

            self.code_text.SetLabelText( self.code )

            te_p = self.provider_text.GetTextExtent( self.entry.GetProvider() )
            te_a = self.account_text.GetTextExtent( self.entry.GetAccount() )
            self.label_width = te_p[0]
            if te_a[0] > self.label_width:
                self.label_width = te_a[0]
                te_p = ( te_a[0], te_p[1] )

            self.provider_text.SetLabelText( self.entry.GetProvider() )
            self.provider_text.SetClientSize( te_p )
            self.provider_text.SetMinClientSize( te_p )
            self.account_text.SetLabelText( self.entry.GetAccount() )
            self.account_text.SetClientSize( te_p )
            self.account_text.SetMinClientSize( te_p )

            self.GetSizer().Fit( self )

            logging.debug( "AEP UC provider size: %s", str( self.provider_text.GetSize() ) )
            logging.debug( "AEP UC account size:  %s", str( self.account_text.GetSize() ) )
            logging.debug( "AEP UC label width:   %d", self.label_width )
            logging.debug( "AEP UC panel size:    %s", str( self.GetSize() ) )


    def ChangeContents( self ):
        logging.debug( "AEP CC" )
        self.UpdateContents()
        gp = self.GetGrandParent()
        if gp != None:
            logging.debug( "AEP CC notifying frame" )
            gp.UpdatePanelSize()
