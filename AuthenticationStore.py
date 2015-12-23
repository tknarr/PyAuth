# -*- coding: utf-8 -*-

import os
import errno
import random
import logging
import wx

# The authentication store works in tandem with the authentication entry panels. Each
# panel contains a reference to an AuthenticationEntry object in the entry_list in the
# authentication store. In an AuthenticationEntry object, the entry_group holds the number
# used as the group in the config file holding that entry's values. sort_index controls
# the order entries appear in in the main window. The sort_index is altered as entries
# change position in the main window and just before the store is saved. The entry_group
# value is assigned when a new entry is created and doesn't change after that except
# during a regroup operation just before the store is saved.

class AuthenticationStore:

    def __init__( self, filename ):
        self.cfg = wx.FileConfig( 'PyAuth', "Silverglass Technical", localFilename = filename,
                                  style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        cfgfile = wx.FileConfig.GetLocalFileName( 'database.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        logging.info( "Database file: %s", cfgfile )
        random.seed() # TODO Remove after proper GenerateNextCode() implemented
        self.entry_list = []
        self.next_group = 1
        self.next_index = 1

        # Read configuration entries into a list
        # Make sure to update next_group and next_index if we encounter
        #     a larger value for them than we've seen yet
        self.cfg.SetPath( '/entries' )
        more, value, index = self.cfg.GetFirstGroup()
        while more:
            entry_group = int( value )
            logging.debug( "AS reading group %d", entry_group )
            if entry_group > 0:
                if entry_group > self.next_group:
                    self.next_group = entry_group
                cfgpath = '%s/' % entry_group
                sort_index = self.cfg.ReadInt( cfgpath + 'sort_index' )
                logging.debug( "AS   sort index %d", sort_index )
                if sort_index > self.next_index:
                    self.next_index = sort_index
                provider = self.cfg.Read( cfgpath + 'provider' )
                account = self.cfg.Read( cfgpath + 'account' )
                logging.debug( "AS   provider %s", provider )
                logging.debug( "AS   account %s", account )
                secret = self.cfg.Read( cfgpath + 'secret' )
                original_label = self.cfg.Read( cfgpath + 'original_label', '' )
                if original_label == '':
                    original_label = provider + ':' + account
                entry = AuthenticationEntry( entry_group, sort_index, provider, account, secret, original_label )
                self.entry_list.append( entry )
            more, value, index = self.cfg.GetNextGroup(index)
        self.cfg.SetPath( '/' )
        self.next_group += 1
        self.next_index += 1
        logging.debug( "AS next group %d", self.next_group )
        logging.debug( "AS next index %d", self.next_index )

        # Make sure they're sorted at the start
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        

    def EntryList( self ):
        return self.entry_list


    def Save( self ):
        logging.debug( "AS saving all" )
        for entry in self.entry_list:
            entry.Save( self.cfg )
        self.cfg.Flush()
        # Make sure our database of secrets is only accessible by us
        # This should be handled via SetUmask(), but it's not implemented in the Python bindings
        cfgfile = wx.FileConfig.GetLocalFileName( 'database.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        try:
            os.chmod( cfgfile, 0600 )
        except OSError as e:
            if e.errno != errno.ENOENT:
                logging.warning( "Problem with database file %s", cfgfile )
                logging.warning( "Error code %d: %s ", e.errno, e.strerror )


    def Reindex( self ):
        logging.debug( "AS reindexing" )
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        i = 1;
        for e in self.entry_list:
            e.SetIndex( i )
            i += 1
        self.next_index = i
        logging.debug( "AS next index = %d", self.next_index )

    
    def Regroup( self ):
        logging.debug( "AS regroup" )
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        self.cfg.DeleteGroup( '/entries' )
        i = 1
        for e in self.entry_list:
            e.SetGroup( i )
            e.SetIndex( i )
            e.Save( self.cfg )
            i += 1
        self.next_group = i
        self.next_index = i
        logging.debug( "AS next group and index = %d", i )


    def Add( self, provider, account, secret, original_label = None ):
        f = lambda x: x.GetProvider() == provider and x.GetAccount() == account
        elist = filter( f, self.entry_list )
        if len( elist ) > 0:
            logging.warning( "Entry already exists for %s:%s", provider, account )
            return None
        logging.debug( "AS adding new entry %s:%s, group %d, sort index %d",
                       provider, account, self.next_group, self.next_index )
        entry = AuthenticationEntry( self.next_group, self.next_index, provider, account, secret, original_label )
        self.entry_list.append( entry )
        self.next_index += 1
        self.next_group += 1
        entry.Save( self.cfg )
        return entry


    def Delete( self, entry_group ):
        logging.debug( "AS deleting entry %d", entry_group )
        # Have to run the list in reverse so deletions don't change the indexes of upcoming entries
        # TODO More efficient way of doing this
        for i in range( len( self.entry_list ) - 1, -1, -1 ):
            entry = self.entry_list[i]
            if entry.GetGroup() == entry_group:
                logging.debug( "AS deleted entry %d", entry_group )
                self.cfg.DeleteGroup( '/entries/%s' % entry.entry_group )
                del self.entry_list[i]


    def Update( self, entry_group, provider = None, account = None, secret = None, original_label = None ):
        logging.debug( "AS updating entry %d", entry_group )
        f = lambda x: x.GetGroup() == entry_group
        elist = filter( f, self.entry_list )
        if len( elist ) < 1:
            return 0 # No entry found
        if len( elist ) > 1:
            logging.error( "AS %d duplicates of entry %d found, database likely corrupt",
                           len( elist ), entry_group )
            return -1
        entry = elist[0]
        if provider != None:
            logging.debug( "AS new provider %s", provider )
            entry.SetProvider( provider )
        if account != None:
            logging.debug( "AS new account %s", account )
            entry.SetAccount( account )
        if secret != None:
            logging.debug( "AS new secret %s", secret )
            entry.SetSecret( secret )
        if original_label != None:
            logging.debug( "AS new original label %s", original_label )
            entry.SetOriginalLabel( original_label )
        entry.Save( self.cfg )
        return 1
    

class AuthenticationEntry:

    def __init__( self, group, index, provider, account, secret, original_label = None ):
        self.entry_group = group
        self.sort_index = index
        self.provider = provider
        self.account = account
        self.secret = secret
        if original_label != None:
            self.original_label = original_label
        else:
            self.original_label = provider + ':' + account


    def Save( self, cfg ):
        cfgpath = '/entries/%s/' % self.entry_group
        cfg.WriteInt( cfgpath + 'sort_index', self.sort_index )
        cfg.Write( cfgpath + 'provider', self.provider )
        cfg.Write( cfgpath + 'account', self.account )
        cfg.Write( cfgpath + 'secret', self.secret )
        cfg.Write( cfgpath + 'original_label', self.original_label )


    def GetGroup( self ):
        return self.entry_group

    def SetGroup( self, g ):
        self.entry_group = g
        

    def GetSortIndex( self ):
        return self.sort_index

    def SetSortIndex( self, index ):
        self.sort_index = index

    def GetProvider( self ):
        return self.provider
    
    def SetProvider( self, provider ):
        self.provider = provider

    def GetAccount( self ):
        return self.account
    
    def SetAccount( self, account ):
        self.account = account

    def GetOriginalLabel( self ):
        return self.original_label

    def SetOriginalLabel( self, original_label ):
        self.original_label = original_label

    def GetSecret( self ):
        return self.secret
    
    def SetSecret( self, secret ):
        self.secret = secret


    def GenerateNextCode( self ):
        # TODO Generate next TOTP code
        # Random 6-digit number, zero-filled on left
        r = random.randint( 0, 999999 )
        c = "{:0>6d}".format( r )
        return c
