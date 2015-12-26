# -*- coding: utf-8 -*-

import logging
import wx
import Configuration
from AuthenticationStore import AuthenticationStore
from AuthEntryPanel import AuthEntryPanel as AuthEntryPanel
from About import GetAboutInfo
from NewEntryDialog import NewEntryDialog as NewEntryDialog
from UpdateEntryDialog import UpdateEntryDialog as UpdateEntryDialog

class AuthFrame( wx.Frame ):

    def __init__( self, parent, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize,
                  style = wx.DEFAULT_FRAME_STYLE, name = wx.FrameNameStr ):
        wx.Frame.__init__( self, parent, id, title, pos, size, style, name )
        logging.debug( "AF init" )

        self.entries_window = None
        self.auth_store = None
        self.entry_panels = []
        self.visible_entries = Configuration.GetNumberOfItemsShown()
        self.entry_height = 0    # Height of tallest panel
        self.entry_width = 0     # Width of widest panel
        self.label_width = 0     # Width of widest label

        # Internal values
        self.entry_border = 2
        self.scrollbar_width = 0
        self.selected_panel = None
        self.show_timers = Configuration.GetShowTimers()
        self.show_all_codes = Configuration.GetShowAllCodes()
        self.show_toolbar = Configuration.GetShowToolbar()

        self.toolbar = None
        self.tool_ids = {}
        self.toolbar_icon_size = Configuration.GetToolIconSize()
        self.new_entry_dialog = None
        self.update_entry_dialog = None

        self.auth_store = AuthenticationStore( Configuration.GetDatabaseFilename() )
        self.since_idle = wx.GetUTCTime()

        # Timers are scarce on some platforms, so we set one up here and broadcast the
        # resulting timer event to all our entry panels for processing. That also simplifies
        # shutdown. The timer will tick roughly once per second. The higher the precision the
        # better, but since we're using absolute times to generate codes rather than counting
        # ticks the precision isn't horribly critical beyond being good enough to keep the UI
        # from being too far out-of-sync with the wall clock second hand.
        self.timer = wx.Timer( self )
        self.iconized = True # Start off iconized for timer purposes, set correctly in OnCreate

        self.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
        menu_bar = self.create_menu_bar()
        self.SetMenuBar( menu_bar )
        self.toolbar = self.create_toolbar()
        # TODO Hide toolbar if not shown
        self.entries_window = self.create_entries_window()
        self.GetSizer().Add( self.entries_window, 1, 0, 0 )

        # Get scrollbar width so we can account for it in window sizing
        # Turns out for layout we don't need to adjust for this
        self.scrollbar_width = wx.SystemSettings.GetMetric( wx.SYS_VSCROLL_X, self.entries_window )
        ## logging.debug( "AF scrollbar width = %d", self.scrollbar_width )

        self.populate_entries_window()
        self.UpdatePanelSize()

        # Window event handlers
        self.Bind( wx.EVT_WINDOW_CREATE, self.OnCreate )
        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
        self.Bind( wx.EVT_SIZE, self.OnSize )
        self.Bind( wx.EVT_TIMER, self.OnTimerTick )
        self.Bind( wx.EVT_ICONIZE, self.OnIconize )
        ## TODO self.KeyBind( wx.EVT_CHAR, self.OnKey )
        ## self.Bind( wx.EVT_IDLE, self.OnIdle ) # Debugging sizing only
        # Menu event handlers
        self.Bind( wx.EVT_MENU, self.OnMenuNewEntry,     id = wx.ID_NEW )
        self.Bind( wx.EVT_MENU, self.OnMenuReindex,      id = self.MENU_REINDEX )
        self.Bind( wx.EVT_MENU, self.OnMenuRegroup,      id = self.MENU_REGROUP )
        self.Bind( wx.EVT_MENU, self.OnMenuQuit,         id = wx.ID_EXIT )
        self.Bind( wx.EVT_MENU, self.OnMenuCopyCode,     id = self.MENU_COPY_CODE )
        self.Bind( wx.EVT_MENU, self.OnMenuEditEntry,    id = wx.ID_EDIT )
        self.Bind( wx.EVT_MENU, self.OnMenuDeleteEntry,  id = wx.ID_DELETE )
        self.Bind( wx.EVT_MENU, self.OnMenuMoveUp,       id = wx.ID_UP )
        self.Bind( wx.EVT_MENU, self.OnMenuMoveDown,     id = wx.ID_DOWN )
        self.Bind( wx.EVT_MENU, self.OnMenuShowTimers,   id = self.MENU_SHOW_TIMERS )
        self.Bind( wx.EVT_MENU, self.OnMenuShowAllCodes, id = self.MENU_SHOW_ALL_CODES )
        self.Bind( wx.EVT_MENU, self.OnMenuShowToolbar,  id = self.MENU_SHOW_TOOLBAR )
        self.Bind( wx.EVT_MENU, self.OnMenuHelpContents, id = wx.ID_HELP )
        self.Bind( wx.EVT_MENU, self.OnMenuAbout,        id = wx.ID_ABOUT )
        # Any toolbar tool handlers that aren't also menu item handlers go below here


    def KeyBind( self, event_type, func ):
        self.Bind( event_type, func )
        self.entries_window.Bind( event_type, func )
        for panel in self.entry_panels:
            panel.Bind( event_type, func )


    def OnCreate( self, event ):
        self.Unbind( wx.EVT_WINDOW_CREATE )
        logging.debug( "AF created" )
        self.iconized = self.IsIconized()
        self.timer.Start( 1000 )
        self.Refresh()


    def OnSize( self, event ):
        # Need this to keep the size of the window in entries updated as it's resized
        new_size = self.WindowToClientSize( event.GetSize() )
        self.visible_entries = self.CalcItemsShown( new_size.GetHeight() )
        event.Skip()


    def OnTimerTick( self, event ):
        # Make sure we don't broadcast any more timer ticks after shutdown
        # even if we do get called by straggling tick events. We also don't
        # need to update entry panels while we're minimized.
        if self.timer != None and not self.iconized:
            # Broadcast the event to all entry panels for processing
            for panel in self.entry_panels:
                panel.QueueEvent( event.Clone() )


    def OnIdle( self, event ):
        now = wx.GetUTCTime()
        t = now - self.since_idle
        if t > 5:
            self.since_idle = now
            logging.debug( "IDLE FR window size %s min %s",
                           self.GetSize(), self.GetMinSize() )
            logging.debug( "IDLE FR client size %s min %s",
                           self.GetClientSize(), self.GetMinClientSize() )
            logging.debug( "IDLE EW window size %s min %s",
                           self.entries_window.GetSize(), self.entries_window.GetMinSize() )
            logging.debug( "IDLE EW client size %s min %s",
                           self.entries_window.GetClientSize(), self.entries_window.GetMinClientSize() )


    def OnIconize( self, event ):
        was_iconized = self.iconized
        self.iconized = event.IsIconized()
        ## if was_iconized and not self.iconized:
        # TODO Generate an immediate fake timer tick to update the countdown
        event.Skip()


    def OnKey( self, event ):
        key = event.GetUnicodeKey()
        if key == WXK_NONE:
            key = event.GetKeyCode()
        logging.debug( "AF OnKey code %d", key )
        # The Escape key deselects any selected entry
        if key == wx.WXK_ESCAPE:
            if self.selected_panel != None:
                self.selected_panel.Deselect()
                self.selected_panel = None
        elif key == wx.WXK_UP or key == wx.WXK_DOWN or key == wx.WXK_NUMPAD_UP or key == wx.WXK_NUMPAD_UP:
            if not event.HasModifiers():
                logging.debug( "AF OnKey up/down key" )
                # TODO Alone, Up/Down arrow keys change the selected panel
            elif event.HasModifiers() == wx.MOD_CONTROL:
                logging.debug( "AF OnKey Control-up/down key" )
                # TODO With Control key, move entries up/down in the list
        elif key == wx.WXK_DELETE or key == wx.WXK_NUMPAD_DELETE:
            if not event.HasModifiers():
                logging.debug( "AF OnKey delete key" )
                # TODO Delete key deletes the selected entry
        # TODO other keycodes
        event.Skip()


    def OnCloseWindow( self, event ):
        logging.debug( "AF close window" )
        self.timer.Stop()
        self.Unbind( wx.EVT_TIMER )
        self.timer = None
        self.auth_store.Save()
        wp = self.GetPosition()
        Configuration.SetLastWindowPosition( wp )
        ## logging.debug( "AF entries window size = %s, min = %s", self.entries_window.GetSize(),
        ##                self.entries_window.GetMinSize() )
        ## logging.debug( "AF window client size = %s, min = %s", self.GetClientSize(),
        ##                self.GetMinClientSize() )
        self.visible_entries = self.CalcItemsShown( self.GetClientSize().GetHeight() )
        logging.debug( "AF visible items %d", self.visible_entries )
        Configuration.SetNumberOfItemsShown( self.visible_entries )
        Configuration.SetShowTimers( self.show_timers )
        Configuration.SetShowAllCodes( self.show_all_codes )
        Configuration.Save()
        if self.new_entry_dialog != None:
            self.new_entry_dialog.Destroy()
        if self.update_entry_dialog != None:
            self.update_entry_dialog.Destroy()
        self.Destroy()


    def OnMenuQuit( self, event ):
        logging.debug( "AF menu Quit command" )
        self.Close()

    def OnMenuNewEntry( self, event ):
        logging.debug( "AF menu New Entry command" )
        if self.new_entry_dialog == None:
            self.new_entry_dialog = NewEntryDialog( self, wx.ID_ANY, "New Entry" )
        self.new_entry_dialog.Reset()

        result = self.new_entry_dialog.ShowModal()
        if result == wx.ID_OK:
            logging.debug( "AF NE creating new entry" )
            provider = self.new_entry_dialog.GetProviderValue()
            account = self.new_entry_dialog.GetAccountValue()
            secret = self.new_entry_dialog.GetSecretValue()
            original_label = self.new_entry_dialog.GetOriginalLabel()
            if original_label == '':
                original_label = provider + ':' + account
            logging.debug( "AF NE provider %s", provider )
            logging.debug( "AF NE account  %s", account )
            logging.debug( "AF NE secret   %s", secret )
            logging.debug( "AF NE orig lbl %s", original_label )
            entry = self.auth_store.Add( provider, account,secret, original_label )
            if entry != None:
                logging.debug( "AF NE new panel: %d", entry.GetGroup() )
                # If all we have is the dummy entry then replace it, otherwise add the new entry at the end
                if len( self.entry_panels ) == 1 and self.entry_panels[0].GetEntry() == None:
                    panel = self.entry_panels[0]
                    panel.SetEntry( entry )
                    logging.debug( "AF NE replaced dummy panel with: %s", panel.GetName() )
                else:
                    panel = AuthEntryPanel( self.entries_window, wx.ID_ANY, style = wx.BORDER_THEME, entry = entry )
                    self.entry_panels.append( panel )
                    logging.debug( "AF NE add panel: %s", panel.GetName() )
                    self.entries_window.GetSizer().Add( panel, 0, wx.ALL | wx.ALIGN_LEFT, self.entry_border )
                ## logging.debug( "AF NE panel size %s min %s", str( panel.GetSize() ), str( panel.GetMinSize() ) )
                self.UpdatePanelSize()
            else:
                logging.debug( "AF NE duplicate item" )
                wx.Bell()
                dlg = wx.MessageDialog( self, "That entry already exists.", "Error",
                                        style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE )
                dlg.SetExtendedMessage( "Provider: %s\nAccount: %s" % ( provider, account ) )
                dlg.ShowModal()
                dlg.Destroy()

    def OnMenuEditEntry( self, event ):
        logging.debug( "AF menu Edit Entry command" )
        if self.update_entry_dialog == None:
            self.update_entry_dialog = UpdateEntryDialog( self, wx.ID_ANY, "Edit Entry" )
        entry = None
        if self.selected_panel == None:
            wx.Bell()
            dlg = wx.MessageDialog( self, "No entry selected.", "Error",
                                    style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE )
            dlg.SetExtendedMessage( "You must select an entry to edit." )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            entry = self.selected_panel.GetEntry()
        if entry == None:
            self.OnMenuNewEntry( event ) # Dummy panel selected, create a new entry instead
        else:
            self.update_entry_dialog.Reset( entry.GetProvider(), entry.GetAccount(), entry.GetSecret() )
            result = self.update_entry_dialog.ShowModal()
            if result == wx.ID_OK:
                provider = self.update_entry_dialog.GetProviderValue()
                account = self.update_entry_dialog.GetAccountValue()
                secret = self.update_entry_dialog.GetSecretValue()
                if provider == entry.GetProvider():
                    provider = None
                if account == entry.GetAccount():
                    account = None
                if secret == entry.GetSecret():
                    secret = None
                if provider != None or account != None or secret != None:
                    logging.debug( "AF UE updating entry" )
                    status = self.auth_store.Update( entry.GetGroup(), provider, account, secret )
                    if status < 0:
                        wx.Bell()
                        dlg = wx.MessageDialog( self, "Database is corrupted.", "Error",
                                                style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE )
                        dlg.SetExtendedMessage( "Multiple copies of the entry were found.\n" +
                                                "The database is likely corrupted and needs repaired." )
                        dlg.ShowModal()
                        dlg.Destroy()
                    elif status == 0:
                        dlg = wx.MessageDialog( self, "Entry not found.", "Error",
                                                style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE )
                        dlg.SetExtendedMessage( "The entry was not found in the database.\n" +
                                                "This should not have happened." )
                        dlg.ShowModal()
                        dlg.Destroy()
                    else:
                        self.selected_panel.ChangeContents()
                        ## logging.debug( "AF UE panel size %s min %s", str( panel.GetSize() ),
                        ##                str( panel.GetMinSize() ) )
                        self.UpdatePanelSize()

    def OnMenuDeleteEntry( self, event ):
        logging.debug( "AF menu Delete Entry command" )
        if self.selected_panel != None:
            logging.debug( "AF DE deleting panel %s", self.selected_panel.GetName() )
            panel = self.selected_panel
            self.selected_panel = None
            # Remove the panel from the entries list and the entries window
            self.entry_panels.remove( panel )
            status = self.entries_window.GetSizer().Detach( panel )
            if not status:
                logging.warning( "Could not remove %s from entries window", panel.GetName() )
            ## logging.debug( "AF UE panel size %s min %s", str( panel.GetSize() ),
            ##                str( panel.GetMinSize() ) )
            self.UpdatePanelSize()
            # Delete the panel's entry in the authentication store
            entry = panel.GetEntry()
            if entry != None:
                self.auth_store.Delete( entry.GetGroup() )
        else:
            dlg = wx.MessageDialog( self, "No entry selected.", "Error",
                                    style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP | wx.CENTRE )
            dlg.SetExtendedMessage( "You must select an entry to delete." )
            dlg.ShowModal()
            dlg.Destroy()
            

    def OnMenuCopyCode( self, event ):
        logging.warning( "AF tool CopyCode command" )
        # TODO Copy code from selected panel to clipboard


    def OnMenuMoveUp( self, event ):
        logging.debug( "AF menu Move Up command" )
        if self.selected_panel != None:
            i = self.entry_panels.index( self.selected_panel )
            if i > 0 and i < len( self.entry_panels ):
                logging.debug( "AF moving entry %d up", i )
                # Swap the selected panel with the one before it in the list by popping it
                # and inserting it one position before it's previous location, then swap the
                # sort indexes of the two panels we switched around.
                tgt = self.entry_panels.pop(i)
                self.entry_panels.insert( i-1, tgt )
                si = self.entry_panels[i].GetSortIndex()
                self.entry_panels[i].SetSortIndex( self.entry_panels[i-1].GetSortIndex() )
                self.entry_panels[i-1].SetSortIndex( si )
                # Then visually update the list by swapping the items in the sizer
                sts = self.entries_window.GetSizer().Remove( i )
                if sts:
                    self.entries_window.GetSizer().Insert( i-1, tgt, 0, wx.ALL | wx.ALIGN_LEFT,
                                                           self.entry_border )
                    self.SendSizeEvent()
                else:
                    logging.warning( "Error removing item %d from entries window. Recovering.", i )
                    self.depopulate_entries_window()
                    self.populate_entries_window()
                    self.UpdatePanelSize()
            else:
                logging.debug( "AF entry %d out-of-range", i )
                wx.Bell()

    def OnMenuMoveDown( self, event ):
        logging.debug( "AF menu Move Down command" )
        if self.selected_panel != None:
            i = self.entry_panels.index( self.selected_panel )
            if i >= 0 and i < len( self.entry_panels ) - 1:
                logging.debug( "AF moving entry %d down", i )
                # Swap the selected panel with the one after it in the list by popping the
                # one after it and inserting that one back at the selected panel's position,
                # then swap the sort indexes of the two panels we switched around.
                tgt = self.entry_panels.pop(i+1)
                self.entry_panels.insert( i, tgt )
                si = self.entry_panels[i+1].GetSortIndex()
                self.entry_panels[i+1].SetSortIndex( self.entry_panels[i].GetSortIndex() )
                self.entry_panels[i].SetSortIndex( si )
                # Then visually update the list by swapping the items in the sizer
                sts = self.entries_window.GetSizer().Remove( i+1 )
                if sts:
                    self.entries_window.GetSizer().Insert( i, tgt, 0, wx.ALL | wx.ALIGN_LEFT,
                                                           self.entry_border )
                    self.SendSizeEvent()
                else:
                    logging.warning( "Error removing item %d from entries window. Recovering.", i )
                    self.depopulate_entries_window()
                    self.populate_entries_window()
                    self.UpdatePanelSize()
            else:
                logging.debug( "AF entry %d out-of-range", i )
                wx.Bell()

    def OnMenuShowTimers( self, event ):
        # TODO menu handler
        logging.warning( "Show Timers" )

    def OnMenuShowAllCodes( self, event ):
        # TODO menu handler
        logging.warning( "Show All Codes" )

    def OnMenuShowToolbar( self, event ):
        # TODO menu handler
        logging.warning( "Show Toolbar" )

    def OnMenuHelpContents( self, event ):
        # TODO menu handler
        logging.warning( "Help Contents" )

    def OnMenuAbout( self, event ):
        logging.debug( "AF menu About dialog" )
        info = GetAboutInfo( wx.ClientDC( self ) )
        wx.AboutBox( info )

    def OnMenuReindex( self, event ):
        logging.debug( "AF menu Reindex command" )
        logging.info( "Database reindex ordered" )
        self.auth_store.Reindex()
        self.depopulate_entries_window()
        self.populate_entries_window()
        self.UpdatePanelSize()

    def OnMenuRegroup( self, event ):
        logging.debug( "AF menu Regroup command" )
        logging.info( "Database regroup and reindex ordered" )
        self.auth_store.Regroup()
        self.depopulate_entries_window()
        self.populate_entries_window()
        self.UpdatePanelSize()


    def create_menu_bar( self ):
        logging.debug( "AF create menu bar" )
        mb = wx.MenuBar()

        menu = wx.Menu()
        menu.Append( wx.ID_NEW, "&New", "Create a new entry" )
        mi = wx.MenuItem( menu, wx.ID_ANY, "Reindex", "Regenerate sort indexes in current order" )
        self.MENU_REINDEX = mi.GetId()
        menu.AppendItem( mi )
        mi = wx.MenuItem( menu, wx.ID_ANY, "Regroup", "Completely compact database in current order" )
        self.MENU_REGROUP = mi.GetId()
        menu.AppendItem( mi )
        menu.AppendSeparator()
        menu.Append( wx.ID_EXIT, "E&xit", "Exit the program" )
        mb.Append( menu, "&File" )
        
        menu = wx.Menu()
        mi = wx.MenuItem( menu, wx.ID_ANY, "&Copy code", "Copy current code to clipboard" )
        self.MENU_COPY_CODE = mi.GetId()
        mi_icon = wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_MENU )
        mi.SetBitmap( mi_icon )
        menu.AppendItem( mi )
        menu.AppendSeparator()
        menu.Append( wx.ID_EDIT, "&Edit", "Edit the selected entry" )
        menu.Append( wx.ID_DELETE, "&Delete", "Delete the selected entry" )
        menu.AppendSeparator()
        menu.Append( wx.ID_UP, "Move Up", "Move the selected entry up one position" )
        menu.Append( wx.ID_DOWN, "Move Down", "Move the selected entry down one position" )
        mb.Append( menu, "Edit" )
        
        menu = wx.Menu()
        mi = wx.MenuItem( menu, wx.ID_ANY, "Timers", "Show timer bars", kind = wx.ITEM_CHECK )
        self.MENU_SHOW_TIMERS = mi.GetId()
        menu.AppendItem( mi )
        menu.Check( self.MENU_SHOW_TIMERS, self.show_timers )
        mi = wx.MenuItem( menu, wx.ID_ANY, "All Codes", "Show codes for all entries", kind = wx.ITEM_CHECK )
        self.MENU_SHOW_ALL_CODES = mi.GetId()
        menu.AppendItem( mi )
        menu.Check( self.MENU_SHOW_ALL_CODES, self.show_all_codes )
        mi = wx.MenuItem( menu, wx.ID_ANY, "Toolbar", "Show the toolbar", kind = wx.ITEM_CHECK )
        self.MENU_SHOW_TOOLBAR = mi.GetId()
        menu.AppendItem( mi )
        menu.Check( self.MENU_SHOW_TOOLBAR, self.show_toolbar )
        mb.Append( menu, "&View" )
        
        menu = wx.Menu()
        menu.Append( wx.ID_HELP, "&Help", "Help index" )
        menu.Append( wx.ID_ABOUT, "About", "About PyAuth" )
        mb.Append( menu, "Help" )
        
        return mb


    def create_toolbar( self ):
        toolbar = self.CreateToolBar( name = 'tool_bar' )
        toolbar.SetToolBitmapSize( self.toolbar_icon_size )

        self.tool_ids = {}
        
        tool_icon = wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_TOOLBAR, self.toolbar_icon_size )
        tool = toolbar.AddTool( self.MENU_COPY_CODE, tool_icon,
                                shortHelpString = "Copy selected code to clipboard" )
        self.tool_ids['COPYCODE'] = tool.GetId()

        toolbar.AddSeparator()

        tool_icon = wx.ArtProvider.GetBitmap( wx.ART_GO_UP, wx.ART_TOOLBAR, self.toolbar_icon_size )
        tool = toolbar.AddTool( wx.ID_UP, tool_icon,
                                shortHelpString = "Move selected entry up one position" )
        self.tool_ids['MOVE_UP'] = tool.GetId()

        tool_icon = wx.ArtProvider.GetBitmap( wx.ART_GO_DOWN, wx.ART_TOOLBAR, self.toolbar_icon_size )
        tool = toolbar.AddTool( wx.ID_DOWN, tool_icon,
                                shortHelpString = "Move selected entry down one position" )
        self.tool_ids['MOVE_DOWN'] = tool.GetId()

        toolbar.Realize()
        
        return toolbar


    def create_entries_window( self ):
        logging.debug( "AF create entries window" )
        sw = wx.ScrolledWindow( self, wx.ID_ANY, style = wx.VSCROLL, name = 'entries_window' )
        sw.ShowScrollbars( wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT )
        sw.EnableScrolling( False, True )
        sw.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
        return sw


    def populate_entries_window( self ):
        logging.debug( "AF populating the entries window" )
        # Create our entry item panels and put them in the scrollable window
        self.entry_panels = []
        for entry in self.auth_store.EntryList():
            logging.debug( "AF create panel: %d", entry.GetGroup() )
            panel = AuthEntryPanel( self.entries_window, wx.ID_ANY, style = wx.BORDER_THEME,
                                    entry = entry )
            self.entry_panels.append( panel )
        if len( self.entry_panels ) > 0:
            # Make sure they're sorted at the start
            keyfunc = lambda x: x.GetSortIndex()
            self.entry_panels.sort( key = keyfunc )
        else:
            # Add dummy entry. We need at least this to be able to size things properly. We'll
            # replace it with the first real entry.
            self.entry_panels.append( AuthEntryPanel( self.entries_window, wx.ID_ANY,
                                                      style = wx.BORDER_THEME ) )
        for panel in self.entry_panels:
            logging.debug( "AF add panel: %d - %s", panel.GetSortIndex(), panel.GetName() )
            ## logging.debug( "AF panel size %s min %s", str( panel.GetSize() ), str( panel.GetMinSize() ) )
            self.entries_window.GetSizer().Add( panel, 0, wx.ALL | wx.ALIGN_LEFT, self.entry_border )


    def depopulate_entries_window( self ):
        logging.debug( "AF depopulating the entries window" )
        # Clear out the entries window sizer and then destroy the individual entry panels
        self.entries_window.GetSizer().Clear( False )
        for panel in self.entry_panels:
            logging.debug( "AF destroy panel: %s", panel.GetName() )
            panel.Destroy()
        self.entry_panels = []


    def CalcItemsShown( self, height ):
        ## logging.debug( "AF CIS wcs = %s, entry height = %d", height, self.entry_height )
        # Doing integer math, so we can't cancel terms and add 1/2
        n = height + ( self.entry_height + 2 * self.entry_border ) / 2
        d = self.entry_height + 2 * self.entry_border
        r = n / d
        if r < 1:
            r = 1
        ## logging.debug( "AF CIS result = %d / %d = %d", n, d, r )
        return r


    def AdjustWindowSizes( self ):
        ## logging.debug( "AF AWS entry size:  %dx%d, visible = %d", self.entry_width, self.entry_height,
        ##                self.visible_entries )
        # Need to adjust this here, it depends on the entry height which may change
        self.entries_window.SetScrollRate( 0, self.entry_height + 2 * self.entry_border )

        # Finagle this to keep things consistent whether we start with a scrollbar visible or not
        # Yeah it's weird, but that's how wxWidgets appears to work
        column_width = self.entry_width + 2 * self.entry_border
        if self.visible_entries >= len( self.entry_panels ):
            column_width += self.scrollbar_width
        # Figure out the window height and minimum height based on entries
        column_height = self.visible_entries * ( self.entry_height + 2 * self.entry_border )
        min_height = self.entry_height + 2 * self.entry_border

        # The size calculations are broken out and made explicit to make sure everything's
        # calculated correctly. We end up not using the client sizes, but we need them
        # as intermediate steps to make sure the frame has a minimum size large enough
        # for it's client area to hold the entries window. Setting the client sizes for
        # the entries window and frame ends up causing glitches where the minimum height
        # can be less than 1 entry panel and the minimum width is a few pixels short of
        # accounting for the scrollbar.
        
        # Calculate size needed in client area of scrolling entries window
        entries_client_size = wx.Size( column_width, column_height )
        entries_min_client_size = wx.Size( column_width, min_height )
        # Convert the client area size to the entries window size
        entries_size = self.entries_window.ClientToWindowSize( entries_client_size )
        entries_min_size = self.entries_window.ClientToWindowSize( entries_min_client_size )

        # Generate correct frame size to hold the entries window in the client area
        frame_size = self.ClientToWindowSize( entries_size )
        frame_min_size = self.ClientToWindowSize( entries_min_size )
        
        ## logging.debug( "AWS FR window size %s min %s", frame_size, frame_min_size )
        ## logging.debug( "AWs EW window size %s min %s", entries_size, entries_min_size )
        ## logging.debug( "AWS EW client size %s min %s", entries_client_size, entries_min_client_size )
        
        # Set window sizes and minimum sizes for the entries window and the frame
        self.entries_window.SetSize( entries_size )
        self.entries_window.SetMinSize( entries_min_size )
        self.SetSize( frame_size )
        self.SetMinSize( frame_min_size )


    def AdjustPanelSizes( self ):
        logging.debug( "AF APS" )
        self.entry_height = 0
        self.entry_width = 0
        self.label_width = 0
        for entry in self.entry_panels:
            # Update max entry panel sizes
            entry_size = entry.GetPanelSize()
            label_width = entry.GetLabelWidth()
            ## logging.debug( "AF APS %s: panel size %s label width %d", entry.GetName(),
            ##                str( entry_size ), label_width )
            if entry_size.GetHeight() > self.entry_height:
                self.entry_height = entry_size.GetHeight()
            if entry_size.GetWidth() > self.entry_width:
                self.entry_width = entry_size.GetWidth()
            if label_width > self.label_width:
                self.label_width = label_width
        ## logging.debug( "AF APS entry size %dx%d label width %d", self.entry_width, self.entry_height,
        ##                self.label_width )
        for entry in self.entry_panels:
            entry.ResizePanel( self.entry_width, self.entry_height, self.label_width )
                

    def UpdatePanelSize( self ):
        self.AdjustPanelSizes()
        self.AdjustWindowSizes()
        self.Refresh()
        self.SendSizeEvent()


    def SelectPanel( self, panel, selected = True ):
        logging.debug( "AF panel %s: %s", panel.GetName(), "select" if selected else "deselect" )
        if selected:
            if self.selected_panel != None:
                self.selected_panel.Deselect()
            panel.Select()
            self.selected_panel = panel
        else:
            panel.Deselect()
            if self.selected_panel != None:
                self.selected_panel.Deselect()
            self.selected_panel = None
