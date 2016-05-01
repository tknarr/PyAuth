# -*- coding: utf-8 -*-

import os
import errno
import string
import base64
import wx
import pyotp
from About import GetProgramName, GetVendorName
from Logging import GetLogger
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

# The authentication store works in tandem with the authentication entry panels. Each
# panel contains a reference to an AuthenticationEntry object in the entry_list in the
# authentication store. In an AuthenticationEntry object, the entry_group holds the number
# used as the group in the config file holding that entry's values. sort_index controls
# the order entries appear in in the main window. The sort_index is altered as entries
# change position in the main window and just before the store is saved. The entry_group
# value is assigned when a new entry is created and doesn't change after that except
# during a regroup operation just before the store is saved.

class AuthenticationStore:

    def __init__( self, filename, password ):
        self.cfg = wx.FileConfig( GetProgramName(), GetVendorName(), localFilename = filename,
                                  style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        cfgfile = wx.FileConfig.GetLocalFileName( 'database.cfg', wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        GetLogger().info( "Database file: %s", cfgfile )
        self.entry_list = []
        self.next_group = 1
        self.next_index = 1
        self.max_digits = 8

        # Set up an RNG object and derive the encryption key from the supplied
        # password. The salt for the key derivation is taken from the database,
        # or generated randomly and stored in the database if not already present.
        self.rng = Random.new()

        # Check the encryption algorithm entry. If it's missing, the database must
        # have cleartext secrets. If we have a password but cleartext secrets, we'll
        # read them without encryption and then properly encrypt them upon saving.
        self.algorithm = self.cfg.Read( '/crypto/algorithm', 'cleartext' )
        self.algorithm_change = False
        self.UpdatePassword( password )
        if not self.CheckPassword( password ):
            raise ValueError( "Invalid password" )

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
                entry = AuthenticationEntry.Load( self.cfg, entry_group, self )
                if self.algorithm_change:
                    entry.modified = True # Make sure we rewrite entries when encryption changes
                sort_index = entry.GetSortIndex()
                ## GetLogger().debug( "AS   sort index %d", sort_index )
                if sort_index >= self.next_index:
                    self.next_index = sort_index + 1
                digits = entry.GetDigits()
                if digits > self.max_digits:
                    self.max_digits = digits
                self.entry_list.append( entry )
            more, value, index = self.cfg.GetNextGroup(index)
        self.cfg.SetPath( '/' )
        GetLogger().info( "%d entries in authentication database", len( self.entry_list ) )
        GetLogger().debug( "AS next group %d", self.next_group )
        GetLogger().debug( "AS next index %d", self.next_index )

        # Make sure they're sorted at the start
        keyfunc = lambda x: x.GetSortIndex()
        self.entry_list.sort( key = keyfunc )


    def UpdatePassword( self, password ):
        if password == None or password == '':
            self.read_cleartext = True
            self.storage_key = None
        else:
            self.read_cleartext = False
            if self.algorithm == 'cleartext':
                self.read_cleartext = True
                self.algorithm = 'AES'
                self.algorithm_change = True
                check_data = unicode( base64.standard_b64encode( self.rng.read( AES.block_size * 4 ) ) )
                check_ciphertext = self.Encrypt( check_data )
                self.cfg.Write( '/crypto/check_data', check_ciphertext )
                h = SHA256.new()
                h.update( check_data )
                check_hash = unicode( base64.standard_b64encode( h.digest() ) )
                self.cfg.Write( '/crypto/check_hash', check_hash )
                self.cfg.Flush()
            salt = self.cfg.Read( '/crypto/salt', '' )
            if salt == '':
                s = self.rng.read( AES.block_size )
                salt = unicode( base64.standard_b64encode( s ) )
                self.cfg.Write( '/crypto/salt', salt )
                self.cfg.Flush()
            self.storage_key = PBKDF2( password, salt, AES.block_size, 10000 )
        return self.EncryptionEnabled()

    def CheckPassword( self ):
        check_ciphertext = self.cfg.Read( '/crypto/check_data', '' )
        if check_ciphertext == '':
            return True
        check_data = self.Decrypt( check_ciphertext )
        h = SHA256.new()
        h.update( check_data )
        check_hash = unicode( base64.standard_b64encode( h.digest() ) )
        stored_hash = self.cfg.Read( '/crypto/check_hash', '' )
        return check_hash == stored_hash


    def EntryList( self ):
        return self.entry_list

    def MaxDigits( self ):
        return self.max_digits

    def EncryptionEnabled( self ):
        return self.algorithm != 'cleartext'


    def Save( self ):
        GetLogger().debug( "AS saving all" )
        for entry in self.entry_list:
            entry.Save( self.cfg, self )
        if self.storage_key == None:
            if self.algorithm != 'cleartext':
                self.cfg.Write( '/crypto/algorithm', 'cleartext' )
        else:
            if self.algorithm_change:
                self.cfg.Write( '/crypto/algorithm', self.algorithm )
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
            e.Save( self.cfg, self )
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
            e.Save( self.cfg, self )
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
        entry.Save( self.cfg, self )
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
        entry.Save( self.cfg, self )
        self.cfg.Flush()
        return 1


    def Encrypt( self, secret ):
        if self.storage_key == None:
            return secret
        iv = self.rng.read( AES.block_size )
        cipher = AES.new( self.storage_key, AES.MODE_CBC, iv )
        excess = len( secret ) % AES.block_size
        if excess > 0:
            cleartext = secret + ( ' ' * ( AES.block_size - excess ) )
        else:
            cleartext = secret
        ciphertext = iv + cipher.encrypt( cleartext )
        return unicode( base64.standard_b64encode( ciphertext ) )


    def Decrypt( self, ciphertext ):
        if self.storage_key == None or self.read_cleartext:
            return ciphertext
        b = base64.standard_b64decode( ciphertext )
        iv = b[0:AES.block_size]
        raw_ciphertext = b[AES.block_size:]
        cipher = AES.new( self.storage_key, AES.MODE_CBC, iv )
        cleartext = cipher.decrypt( raw_ciphertext )
        return unicode( cleartext ).rstrip()


# Helper to create our deletion table for SetSecret()
def make_deltbl():
    tbl = { ord( '-' ) : None }
    for c in string.whitespace:
        tbl[ ord( c ) ] = None
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
        self.modified = True


    def __cmp__( self, other ):
        return cmp( self.entry_group, other.entry_group ) if other != None else -1


    @classmethod
    def Load( klass, cfg, entry_group, auth_store ):
        cfgpath = '/entries/{0:d}/'.format( entry_group )
        old_path = cfg.GetPath()
        cfg.SetPath( cfgpath )
        sort_index = cfg.ReadInt( 'sort_index' )
        provider = cfg.Read( 'provider' )
        account = cfg.Read( 'account' )
        secret = auth_store.Decrypt( cfg.Read( 'secret' ) )
        digits = cfg.ReadInt( 'digits', 6 )
        original_label = cfg.Read( 'original_label', '' )
        if original_label == '':
            original_label = provider + ':' + account
        cfg.SetPath( old_path )
        obj = klass( entry_group, sort_index, provider, account, secret,
                     digits, original_label )
        obj.modified = False # Newly-created objects are modified, ones loaded from the database aren't
        return obj


    def Save( self, cfg, auth_store ):
        if self.modified:
            cfgpath = '/entries/{0:d}/'.format( self.entry_group )
            cfg.Write( cfgpath + 'type', 'totp' )
            cfg.WriteInt( cfgpath + 'sort_index', self.sort_index )
            cfg.Write( cfgpath + 'provider', self.provider )
            cfg.Write( cfgpath + 'account', self.account )
            cfg.Write( cfgpath + 'secret', auth_store.Encrypt( self.secret ) )
            cfg.WriteInt( cfgpath + 'digits', self.digits )
            cfg.Write( cfgpath + 'original_label', self.original_label )
            self.modified = False


    def GetGroup( self ):
        return self.entry_group

    def SetGroup( self, g ):
        self.entry_group = g
        self.modified = True

    def GetSortIndex( self ):
        return self.sort_index

    def SetSortIndex( self, index ):
        self.sort_index = index
        self.modified = True

    def GetProvider( self ):
        return self.provider

    def SetProvider( self, provider ):
        self.provider = provider
        self.modified = True

    def GetAccount( self ):
        return self.account

    def SetAccount( self, account ):
        self.account = account
        self.modified = True

    def GetDigits( self ):
        return self.digits

    def SetDigits( self, digits ):
        self.digits = digits
        self.modified = True

    def GetOriginalLabel( self ):
        return self.original_label

    def SetOriginalLabel( self, original_label ):
        self.original_label = original_label
        self.modified = True

    def GetSecret( self ):
        return self.secret

    def SetSecret( self, secret ):
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
        self.modified = True


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
                GetLogger().error( "%s:%s OTP error: %s", self.provider, self.account, unicode( e ) )
        return c
