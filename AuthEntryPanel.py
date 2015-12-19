# -*- coding: utf-8 -*-

import logging
import wx
from wx import xrc as xrc
from AuthenticationStore import AuthenticationEntry

class AuthEntryPanel( wx.Panel ):

    def __init__( self ):
        p = wx.PrePanel()

        self.entry = None
        self.index = 0
        self.code = ''
        self.label_width = 0
        self.code_width = 0
        self.timer_width = 0

        self.have_controls = False
        self.provider_text = None
        self.account_text = None
        self.code_text = None
        self.timer_gauge = None

        self.PostCreate( p )
        self.Bind( wx.EVT_WINDOW_CREATE, self.OnCreate )


    def _post_init( self ):
        logging.debug( "AEP post-init" )
        self.provider_text = xrc.XRCCTRL( self, 'provider_text' )
        self.account_text = xrc.XRCCTRL( self, 'account_text' )
        self.code_text = xrc.XRCCTRL( self, 'code_text' )
        self.timer_gauge = xrc.XRCCTRL( self, 'timer_gauge' )
        self.have_controls = True

        te = self.code_text.GetTextExtent( '000000' )
        self.code_width = te[0]
        self.code_text.SetSize( te )
        self.code_text.SetMinSize( te )

        self.timer_width = self.timer_gauge.GetSize().GetWidth()
        self.timer_gauge.SetMinSize( self.timer_gauge.GetSize() )

        self.ChangeContents()


    def OnCreate( self, event ):
        self.Unbind( wx.EVT_WINDOW_CREATE )
        self._post_init()
        self.Refresh


    def GetEntry( self ):
        return self.entry

    def SetEntry( self, entry ):
        self.entry = entry
        self.SetName( 'entry_panel_%s' % self.entry.GetGroup() )
        self.index = self.entry.GetSortIndex()
        self.code = self.entry.GenerateNextCode()
        logging.debug( "AEP SE on %s", self.GetName() )
        if self.have_controls:
            self.ChangeContents()


    def GetPanelSize( self ):
        return self.GetSize()

    def SetPanelHeight( self, height ):
        s = self.GetSize()
        s.SetHeight( height )
        self.SetSize( s )
        self.SetMinSize( s )
    
    def GetLabelWidth( self ):
        return self.label_width


    def ResizePanel( self, panel_height, label_width ):
        if self.have_controls:
            logging.debug( "AEP RP updating %s", self.GetName() )
            logging.debug( "AEP RP initial panel %s", str( self.GetSize() ) )
            logging.debug( "AEP RP initial label width %d", self.label_width )
            changed = False
            
            if label_width != self.label_width:
                logging.debug( "AEP RP label width: %d", label_width )
                self.label_width = label_width
                s = self.provider_text.GetSize()
                s.SetWidth( self.label_width )
                self.provider_text.SetSize( s )
                self.provider_text.SetMinSize( s )
                s = self.account_text.GetSize()
                s.SetWidth( self.label_width )
                self.account_text.SetSize( s )
                self.account_text.SetMinSize( s )
                changed = True

            if panel_height != self.GetSize().GetHeight():
                logging.debug( "AEP RP panel height: %d", panel_height )
                self.SetPanelHeight( panel_height )
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
                te_p[0] = te_a[0]

            self.provider_text.SetLabelText( self.entry.GetProvider() )
            self.provider_text.SetSize( te_p )
            self.provider_text.SetMinSize( te_p )
            self.account_text.SetLabelText( self.entry.GetAccount() )
            self.account_text.SetSize( te_p )
            self.account_text.SetMinSize( te_p )

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
