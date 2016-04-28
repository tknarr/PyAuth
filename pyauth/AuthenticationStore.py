# -*- coding: utf-8 -*-

import os
import errno
import string
import wx
import pyotp
from About import GetProgramName, GetVendorName
from Logging import GetLogger

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
        self.cfg = wx.FileConfig( GetProgramName(), GetVendorName(), localFilename = filename,
                                  style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        cfgfile = wx.FileConfig.GetLocalFileName( 'database.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        GetLogger().info( "Database file: %s", cfgfile )
        self.entry_list = []
        self.next_group = 1
        self.next_index = 1
        self.max_digits = 8

        # Read configuration entries into a list
        # Make sure to update next_group and next_index if we encounter
        #     a larger value for them than we've seen yet
        self.cfg.SetPath( '/entries' )
        more, value, index = self.cfg.GetFirstGroup()
        while more:
            entry_group = int( value )
            ## GetLogger().debug( "AS reading group %d", entry_group )
            if entry_group > 0:
                if entry_group >= self.next_group:
                    self.next_group = entry_group + 1
                cfgpath = '{0:d}/'.format( entry_group )
                sort_index = self.cfg.ReadInt( cfgpath + 'sort_index' )
                ## GetLogger().debug( "AS   sort index %d", sort_index )
                if sort_index >= self.next_index:
                    self.next_index = sort_index + 1
                provider = self.cfg.Read( cfgpath + 'provider' )
                account = self.cfg.Read( cfgpath + 'account' )
                ## GetLogger().debug( "AS   provider %s", provider )
                ## GetLogger().debug( "AS   account %s", account )
                secret = self.cfg.Read( cfgpath + 'secret' )
                digits = self.cfg.ReadInt( cfgpath + 'digits', 6 )
                if digits > self.max_digits:
                    self.max_digits = digits
                original_label = self.cfg.Read( cfgpath + 'original_label', '' )
                if original_label == '':
                    original_label = provider + ':' + account
                entry = AuthenticationEntry( entry_group, sort_index, provider, account, secret,
                                             digits, original_label )
                self.entry_list.append( entry )
            more, value, index = self.cfg.GetNextGroup(index)
        self.cfg.SetPath( '/' )
        GetLogger().info( "%d entries in authentication database", len( self.entry_list ) )
        GetLogger().debug( "AS next group %d", self.next_group )
        GetLogger().debug( "AS next index %d", self.next_index )

        # Make sure they're sorted at the start
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )


    def EntryList( self ):
        return self.entry_list

    def MaxDigits( self ):
        return self.max_digits


    def Save( self ):
        GetLogger().debug( "AS saving all" )
        for entry in self.entry_list:
            entry.Save( self.cfg )
        self.cfg.Flush()
        # Make sure our database of secrets is only accessible by us
        # This should be handled via SetUmask(), but it's not implemented in the Python bindings
        cfgfile = wx.FileConfig.GetLocalFileName( 'database.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        try:
            os.chmod( cfgfile, 0o600 )
        except OSError as e:
            if e.errno != errno.ENOENT:
                GetLogger().warning( "Problem with database file %s", cfgfile )
                GetLogger().warning( "Error code %d: %s ", e.errno, e.strerror )


    def Reindex( self ):
        GetLogger().debug( "AS reindexing" )
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        i = 1;
        for e in self.entry_list:
            e.SetSortIndex( i )
            e.Save( self.cfg )
            i += 1
        self.next_index = i
        GetLogger().debug( "AS next index = %d", self.next_index )
        self.cfg.Flush()


    def Regroup( self ):
        GetLogger().debug( "AS regroup" )
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )
        self.cfg.DeleteGroup( '/entries' )
        i = 1
        for e in self.entry_list:
            e.SetGroup( i )
            e.SetSortIndex( i )
            e.Save( self.cfg )
            i += 1
        self.next_group = i
        self.next_index = i
        GetLogger().debug( "AS next group and index = %d", i )
        self.cfg.Flush()


    def Add( self, provider, account, secret, digits = 6, original_label = None ):
        f = lambda x: x.GetProvider() == provider and x.GetAccount() == account
        elist = list( filter( f, self.entry_list ) )
        if len( elist ) > 0:
            GetLogger().warning( "Entry already exists for %s:%s", provider, account )
            return None
        GetLogger().debug( "AS adding new entry %s:%s, group %d, sort index %d",
                           provider, account, self.next_group, self.next_index )
        entry = AuthenticationEntry( self.next_group, self.next_index, provider, account, secret,
                                     digits, original_label )
        self.entry_list.append( entry )
        self.next_index += 1
        self.next_group += 1
        entry.Save( self.cfg )
        self.cfg.Flush()
        return entry


    def Delete( self, entry_group ):
        GetLogger().debug( "AS deleting entry %d", entry_group )
        f = lambda x: x.GetGroup() == entry_group
        elist = list( filter( f, self.entry_list ) )
        for entry in elist:
            index = self.entry_list.index( entry )
            removed = self.entry_list.pop( index )
            GetLogger().debug( "AS deleted entry %d", removed.entry_group )
            self.cfg.DeleteGroup( '/entries/{0:d}'.format( removed.entry_group ) )
        self.cfg.Flush()


    def Update( self, entry_group, provider = None, account = None, secret = None, digits = None,
                original_label = None ):
        GetLogger().debug( "AS updating entry %d", entry_group )
        f = lambda x: x.GetGroup() == entry_group
        elist = list( filter( f, self.entry_list ) )
        if len( elist ) < 1:
            return 0 # No entry found
        if len( elist ) > 1:
            GetLogger().error( "AS %d duplicates of entry %d found, database likely corrupt",
                               len( elist ), entry_group )
            return -1
        entry = elist[0]
        if provider != None:
            GetLogger().debug( "AS new provider %s", provider )
            entry.SetProvider( provider )
        if account != None:
            GetLogger().debug( "AS new account %s", account )
            entry.SetAccount( account )
        if secret != None:
            GetLogger().debug( "AS new secret" )
            entry.SetSecret( secret )
        if digits != None:
            GetLogger().debug( "AS new digits %d", digits )
            entry.SetDigits( digits )
        if original_label != None:
            GetLogger().debug( "AS new original label %s", original_label )
            entry.SetOriginalLabel( original_label )
        entry.Save( self.cfg )
        self.cfg.Flush()
        return 1


# Helper to create our deletion table for SetSecret()
def make_deltbl():
    tbl = { ord( '-' ) : None }
    for c in string.whitespace:
        tbl[ ord(c) ] = None
    return tbl

class AuthenticationEntry:

    # Never changed, so just make it once
    del_tbl = make_deltbl()

    def __init__( self, group, index, provider, account, secret, digits = 6, original_label = None ):
        self.entry_group = group
        self.sort_index = index
        self.provider = provider
        self.account = account
        self.SetSecret( secret )
        self.digits = digits
        if original_label != None:
            self.original_label = original_label
        else:
            self.original_label = provider + ':' + account

        self.auth = pyotp.TOTP( self.secret, self.digits )
        self.otp_problem = False


    def __cmp__( self, other ):
        return cmp( self.entry_group, other.entry_group ) if other != None else -1


    def Save( self, cfg ):
        cfgpath = '/entries/{0:d}/'.format( self.entry_group )
        cfg.Write( cfgpath + 'type', 'totp' )
        cfg.WriteInt( cfgpath + 'sort_index', self.sort_index )
        cfg.Write( cfgpath + 'provider', self.provider )
        cfg.Write( cfgpath + 'account', self.account )
        cfg.Write( cfgpath + 'secret', self.secret )
        cfg.WriteInt( cfgpath + 'digits', self.digits )
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

    def GetDigits( self ):
        return self.digits

    def SetDigits( self, digits ):
        self.digits = digits

    def GetOriginalLabel( self ):
        return self.original_label

    def SetOriginalLabel( self, original_label ):
        self.original_label = original_label

    def GetSecret( self ):
        return self.secret

    def SetSecret( self, secret ):
        self.secret = secret
        # Strip out dashes and whitespace characters that're sometimes put in the
        # text given to the user.
        self.secret = secret.translate( AuthenticationEntry.del_tbl )
        # We shouldn't need to do this, but pyotp has a problem when the
        # secret needs padding so we'll pad it ourselves which works right.
        m = len( self.secret ) % 8
        if m != 0:
            self.secret += '=' * ( 8 - m )
        # Need a new auth object too
        self.auth = pyotp.TOTP( self.secret )
        self.otp_problem = False


    def GetPeriod( self ):
        return 30 # Google Authenticator uses a 30-second period


    def GenerateNextCode( self ):
        if self.otp_problem:
            c = '?' * self.digits
        else:
            try:
                c = self.auth.now()
            except Exception as e:
                c = '?' * self.digits
                self.otp_problem = True
                GetLogger().error( "%s:%s OTP error: %s", self.provider, self.account, str( e ) )
        return c
