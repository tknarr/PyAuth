# -*- coding: utf-8 -*-

import logging
import wx
from wx import xrc as xrc
from AuthenticationStore import AuthenticationEntry

class AuthEntryPanel( wx.Panel ):

    _first_event_type = wx.EVT_WINDOW_CREATE

    def __init__( self ):
        p = wx.PrePanel()

        self.entry = None
        self.index = 0
        self.code = ''
        self.code_size = wx.DefaultSize

        self.have_controls = False
        self.label_panel = None
        self.provider_text = None
        self.account_text = None
        self.code_text = None
        self.timer_gauge = None

        self.PostCreate( p )
        self.Bind( self._first_event_type, self.OnCreate )


    def _post_init( self ):
        logging.debug( "AEP post-init" )
        self.label_panel = xrc.XRCCTRL( self, 'label_panel' )
        self.provider_text = xrc.XRCCTRL( self, 'provider_text' )
        self.account_text = xrc.XRCCTRL( self, 'account_text' )
        self.code_text = xrc.XRCCTRL( self, 'code_text' )
        self.timer_gauge = xrc.XRCCTRL( self, 'timer' )
        self.have_controls = True

        self.code_size = self.code_text.GetTextExtent( "000000" )
        self.code_text.SetSize( self.code_size )
        self.code_text.SetMinSize( self.code_size )

        self.timer_gauge.SetMinSize( self.timer_gauge.GetSize() )

        self.ChangeContents()


    def OnCreate( self, event ):
        self.Unbind( self._first_event_type )
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
            logging.debug( "AEP SE changing contents" )
            self.ChangeContents()
        else:
            self.SetMinSize( self.GetSize() )


    def GetPanelSize( self ):
        return self.GetSize()
    
    def GetLabelWidth( self ):
        w = 0
        if self.label_panel != None:
            w = self.label_panel.GetSize().GetWidth()
        return w


    def ResizePanel( self, panel_size, label_width ):
        if self.have_controls:
            logging.debug( "AEP RP updating %s", self.GetName() )
            changed = False
            
            if label_width != self.label_panel.GetSize().GetWidth():
                logging.debug( "AEP RP label width: %d", label_width )
                lps = self.label_panel.GetSize()
                lps.SetWidth( label_width )
                self.label_panel.SetSize( lps )
                changed = True

            if panel_size != self.GetSize().GetWidth():
                logging.debug( "AEP RP panel size:  %s", str( panel_size ) )
                self.SetSize( panel_size )
                self.SetMinSize( panel_size )
                changed = True


    def UpdateContents( self ):
        if self.entry != None:
            logging.debug( "AEP UC updating %s", self.GetName() )
            self.code_text.SetLabelText( self.code )
            self.provider_text.SetLabelText( self.entry.GetProvider() )
            te = self.provider_text.GetTextExtent( self.entry.GetProvider() )
            self.provider_text.SetMinSize( te )
            self.account_text.SetLabelText( self.entry.GetAccount() )
            te = self.account_text.GetTextExtent( self.entry.GetAccount() )
            self.account_text.SetMinSize( te )
            self.label_panel.GetSizer().Fit( self.label_panel )
            self.GetSizer().Fit( self )
            logging.debug( "AEP UC provider size: %s", str(self.provider_text.GetSize()) )
            logging.debug( "AEP UC account size:  %s", str(self.account_text.GetSize()) )
            logging.debug( "AEP UC label width:   %d", self.label_panel.GetSize().GetWidth() )
            logging.debug( "AEP UC panel size:    %s", str(self.GetSize()) )


    def ChangeContents( self ):
        logging.debug( "AEP CC" )
        self.UpdateContents()
        gp = self.GetGrandParent()
        if gp != None:
            logging.debug( "AEP CC notifying frame" )
            gp.UpdatePanelSize()
