# -*- coding: utf-8 -*-

import wx
from .AuthenticationStore import AuthenticationEntry
from .Logging import GetLogger

class AuthEntryPanel( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr, entry = None ):
        wx.Panel.__init__ ( self, parent, id, pos, size, style, name )

        self.entry = entry
        self.sort_index = 0
        self.code = ''
        self.label_width = 0

        self.left_down = False
        self.selected = False
        self.totp_cycle = 0
        self.totp_period = 30
        self.code_masked = False
        self.timers_shown = True

        self.label_panel = None
        self.provider_text = None
        self.account_text = None
        self.code_text = None
        self.timer_gauge = None

        if entry != None:
            self.SetName( 'entry_panel_%s' % self.entry.GetGroup() )
        else:
            self.SetName( 'entry_panel_X' )
        ## GetLogger().debug( "AEP init %s", self.GetName() )

        # Create panel child controls

        self.provider_font = wx.Font( 10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
        self.account_font = wx.Font( 10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
        self.code_font = wx.Font( 28, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

        sizer = wx.BoxSizer( wx.HORIZONTAL )
        self.SetSizer( sizer )

        self.label_panel = wx.Panel( self, style = wx.BORDER_NONE, name = 'label_panel' )
        label_sizer = wx.BoxSizer( wx.VERTICAL )
        self.label_panel.SetSizer( label_sizer )

        self.provider_text = wx.StaticText( self.label_panel, wx.ID_ANY, "PROVIDER", style = wx.ALIGN_LEFT,
                                            name = 'provider_text' )
        self.provider_text.Wrap( -1 )
        self.provider_text.SetFont( self.provider_font )
        self.provider_text.Fit()
        label_sizer.Add( self.provider_text, 1,
                         wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0 )

        self.account_text = wx.StaticText( self.label_panel, wx.ID_ANY, "ACCOUNT", style = wx.ALIGN_LEFT,
                                           name = 'account_text' )
        self.account_text.Wrap( -1 )
        self.account_text.SetFont( self.account_font )
        self.account_text.Fit()
        label_sizer.Add( self.account_text, 1,
                         wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0 )

        self.label_panel.Fit()
        sizer.Add( self.label_panel, 0, wx.EXPAND | wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 2 )

        self.code_text = wx.StaticText( self, wx.ID_ANY, 'XXXXXX',
                                        style = wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE,
                                        name = 'code_text' )
        self.code_text.Wrap( -1 )
        self.code_text.SetFont( self.code_font )
        self.code_text.Fit()
        self.code_text.SetInitialSize( self.code_text.GetSize() )
        self.code_text.SetMinSize( self.code_text.GetSize() )
        sizer.Add( self.code_text, 0,
                   wx.EXPAND | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE,
                   12 )

        self.totp_period = entry.GetPeriod() if self.entry != None else 30
        self.timer_gauge = wx.Gauge( self, wx.ID_ANY, self.totp_period - 1, size = wx.Size( 30, 15 ),
                                     style = wx.GA_HORIZONTAL, name='timer_gauge' )
        self.timer_gauge.SetValue( self.totp_period - 1 )
        self.timer_gauge.SetMinSize( self.timer_gauge.GetSize() )
        sizer.Add( self.timer_gauge, 0, wx.RIGHT | wx.ALIGN_CENTER, 2 )

        self.UpdateContents()

        if entry != None:
            self.code = self.entry.GenerateNextCode()

        self.Bind( wx.EVT_WINDOW_CREATE, self.OnCreate )
        self.Bind( wx.EVT_TIMER, self.OnTimerTick )
        self.Bind( wx.EVT_ENTER_WINDOW, self.OnMouseEnter )
        self.Bind( wx.EVT_LEAVE_WINDOW, self.OnMouseLeave )
        self.MouseBind( wx.EVT_LEFT_DCLICK, self.OnDoubleClick )
        self.MouseBind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
        self.MouseBind( wx.EVT_LEFT_UP, self.OnLeftUp )

        ## GetLogger().debug( "AEP init done %s", self.GetName() )


    def MouseBind( self, event_type, func ):
        self.Bind( event_type, func )
        self.label_panel.Bind( event_type, func )
        self.provider_text.Bind( event_type, func )
        self.account_text.Bind( event_type, func )
        self.code_text.Bind( event_type, func )


    def __cmp__( self, other ):
        return cmp( self.GetName(), other.GetName() ) if other != None else -1


    def OnCreate( self, event ):
        self.Unbind( wx.EVT_WINDOW_CREATE )
        ## GetLogger().debug( "AEP created" )
        self.ChangeContents()

    def OnTimerTick( self, event ):
        self.UpdateTimerGauge()

    def OnLeftDown( self, event ):
        self.left_down = True
        event.Skip

    def OnLeftUp( self, event ):
        if self.left_down:
            self.left_down = False
            gp = self.GetGrandParent()
            if gp != None:
                gp.SelectPanel( self, not self.selected )
        event.Skip()

    def OnDoubleClick( self, event ):
        self.left_down = False
        gp = self.GetGrandParent()
        if gp != None:
            gp.SelectPanel( self, True )
            # Copy current code to clipboard
            GetLogger().info( "%s copying code to the clipboard.", self.GetName() )
            if not self.CopyCodeToClipboard():
                wx.Bell()
        event.Skip()

    def OnMouseEnter( self, event ):
        self.left_down = False
        event.Skip()

    def OnMouseLeave( self, event ):
        self.left_down = False
        event.Skip()

    def GetEntry( self ):
        return self.entry

    def SetEntry( self, entry ):
        self.entry = entry
        self.sort_index = entry.GetSortIndex()
        self.SetName( 'entry_panel_%s' % self.entry.GetGroup() )
        self.code = self.entry.GenerateNextCode()
        ## GetLogger().debug( "AEP SE on %s", self.GetName() )
        self.ChangeContents()

    def GetSortIndex( self ):
        if self.entry != None:
            self.sort_index = self.entry.GetSortIndex()
        return self.sort_index

    def SetSortIndex( self, index ):
        self.sort_index = index
        if self.entry != None:
            self.entry.SetSortIndex( index )

    def MaskCode( self, state ):
        self.code_masked = state
        if self.code_masked and not self.selected:
            self.code_text.SetLabelText( 'XXXXXX' )
        else:
            self.code_text.SetLabelText( self.code )

    def ShowTimer( self, state ):
        self.show_timer = state
        if self.show_timer:
            self.timer_gauge.Show()
        else:
            self.timer_gauge.Hide()
        # AuthFrame knows to check panel sizes and resize after showing/hiding timers

    def GetPanelSize( self ):
        return self.GetSize()

    def GetLabelWidth( self ):
        w = self.provider_text.GetSize().GetWidth()
        x = self.account_text.GetSize().GetWidth()
        if x > w:
            w = x
        return w


    def SizeLabels( self, label_width ):
        ## GetLogger().debug( "AEP SL new label width %d", label_width )
        self.label_width = label_width

        s = self.label_panel.GetClientSize()
        s.SetWidth( self.label_width )
        self.label_panel.SetMinClientSize( s )
        self.label_panel.SetClientSize( s )
        self.Fit()

    def UpdateContents( self ):
        if self.entry != None:
            ## GetLogger().debug( "AEP UC updating %s", self.GetName() )
            if self.code_masked and not self.selected:
                self.code_text.SetLabelText( 'XXXXXX' )
            else:
                self.code_text.SetLabelText( self.code )

            self.provider_text.SetLabelText( self.entry.GetProvider() )
            self.provider_text.Fit()
            self.account_text.SetLabelText( self.entry.GetAccount() )
            self.account_text.Fit()

        if self.label_width == 0:
            self.label_width = self.GetLabelWidth()

        s = self.label_panel.GetClientSize()
        s.SetWidth( self.label_width )
        self.label_panel.SetMinClientSize( s )
        self.label_panel.SetClientSize( s )
        self.Fit()

        ## GetLogger().debug( "AEP UC provider size: %s", str( self.provider_text.GetSize() ) )
        ## GetLogger().debug( "AEP UC account size:  %s", str( self.account_text.GetSize() ) )
        ## GetLogger().debug( "AEP UC label width:   %d", self.label_width )
        ## GetLogger().debug( "AEP UC panel size:    %s", str( self.GetSize() ) )


    def ChangeContents( self ):
        ## GetLogger().debug( "AEP CC" )
        self.UpdateContents()
        gp = self.GetGrandParent()
        if gp != None:
            ## GetLogger().debug( "AEP CC notifying frame" )
            gp.UpdatePanelSize()


    def Select( self ):
        self.selected = True
        bg = wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT )
        fg = wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT )
        for item in [ self, self.label_panel, self.provider_text, self.account_text,
                      self.code_text, self.timer_gauge ]:
            item.SetBackgroundColour( bg )
            item.SetForegroundColour( fg )
        # We always show the code when selected regardless of code_masked
        self.code_text.SetLabelText( self.code )

    def Deselect( self ):
        self.selected = False
        for item in [ self, self.label_panel, self.provider_text, self.account_text,
                      self.code_text, self.timer_gauge ]:
            item.SetBackgroundColour( wx.NullColour )
            item.SetForegroundColour( wx.NullColour )
        # We can't be selected, so only code_masked matters
        if self.code_masked:
            self.code_text.SetLabelText( 'XXXXXX' )
        else:
            self.code_text.SetLabelText( self.code )
        

    def UpdateTimerGauge( self ):
        current_time = wx.GetUTCTime()
        ## GetLogger().debug( "AEP %s timer tick %d", self.GetName(), current_time ) # LOTS of debug output
        last_cycle = self.totp_cycle
        self.totp_cycle = current_time % self.totp_period
        # If we wrapped around the end of a cycle, update the code and reset the countdown timer gauge
        if self.totp_cycle < last_cycle and self.entry != None:
            self.code = self.entry.GenerateNextCode()
            if self.code_masked and not self.selected:
                self.code_text.SetLabelText( 'XXXXXX' )
            else:
                self.code_text.SetLabelText( self.code )
        # Make our timer gauge count down to zero
        self.timer_gauge.SetValue( self.totp_period - self.totp_cycle - 1 )

    def CopyCodeToClipboard( self ):
        sts = True
        if wx.TheClipboard.Open():
            if  wx.TheClipboard.SetData( wx.TextDataObject( self.code ) ):
                wx.TheClipboard.Flush()
            else:
                GetLogger().error( "%s encountered an error copying the code to the clipboard.", self.GetName() )
                sts = False
            wx.TheClipboard.Close()
        else:
            GetLogger().error( "%s cannot open clipboard.", self.GetName() )
            sts = False
        return sts