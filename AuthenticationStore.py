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
        ## self.cfg.SetUmask( 0077 ) # Set permissions on the database file
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
            if entry_group > 0:
                if entry_group > self.next_group:
                    self.next_group = entry_group
                cfgpath = '%s/' % entry_group
                sort_index = self.cfg.ReadInt( cfgpath + 'sort_index' )
                if sort_index > self.next_index:
                    self.next_index = sort_index
                provider = self.cfg.Read( cfgpath + 'provider' )
                account = self.cfg.Read( cfgpath + 'account' )
                secret = self.cfg.Read( cfgpath + 'secret' )
                original_label = self.cfg.Read( cfgpath + 'original_label', '' )
                if original_label == '':
                    original_label = provider + ':' + account
                entry = AuthenticationEntry( entry_group, sort_index, provider, account, secret, original_label )
                self.entry_list.append( entry )
            more, value, index = self.cfg.GetNextGroup(index)
        self.cfg.SetPath( '/' )

        # Make sure they're sorted at the start
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        

    def EntryList( self ):
        return self.entry_list


    def Save( self ):
        for entry in self.entry_list:
            entry.Save( self.cfg )
        self.cfg.Flush()
        # Make sure our database of secrets is only accessible by us
        cfgfile = wx.FileConfig.GetLocalFileName( 'database.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        try:
            os.chmod( cfgfile, 0600 )
        except OSError as e:
            if e.errno != errno.ENOENT:
                logging.warning( "Problem with database file %s", cfgfile )
                logging.warning( "Error code %d: %s ", e.errno, e.strerror )


    def Reindex( self ):
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        i = 1;
        for e in self.entry_list:
            e.SetIndex( i )
            i += 1
        self.next_index = i

    
    def Regroup( self ):
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


    def Add( self, provider, account, secret, original_label = None ):
        f = lambda x: x.GetProvider() == provider and x.GetAccount() == account
        elist = filter( f, self.entry_list )
        if len( elist ) > 0:
            return None
        entry = AuthenticationEntry( self.next_group, self.next_index, provider, account, secret, original_label )
        self.entry_list.append( entry )
        self.next_index += 1
        self.next_group += 1
        entry.Save( self.cfg )
        return entry


    def Delete( self, entry_group ):
        for i in range( len( self.entry_list ) - 1, -1, -1 ):
            entry = self.entry_list[i]
            if entry.GetGroup() == entry_group:
                self.cfg.DeleteGroup( '/entries/%s' % entry.entry_group )
                del self.entry_list[i]


    def Update( self, entry_group, provider = None, account = None, secret = None, original_label = None ):
        for entry in self.entry_list:
            if entry.GetGroup() == entry_group:
                if provider != None:
                    entry.SetProvider( provider )
                if account != None:
                    entry.SetAccount( account )
                if secret != None:
                    entry.SetSecret( secret )
                if original_label != None:
                    entry.SetOriginalLabel( original_label )
                entry.Save( self.cfg )
                
    
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
