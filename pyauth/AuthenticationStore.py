# -*- coding: utf-8 -*-
"""Authentication secrets store."""

## PyAuth - Google Authenticator desktop application
## Copyright (C) 2016 Todd T Knarr <tknarr@silverglass.org>

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see http://www.gnu.org/licenses/

import os
import errno
import string
import base64
import urllib
import wx
import pyotp
from About import GetProgramName, GetVendorName
from Logging import GetLogger
from Encryption import create_encryption_object, generate_salt
from Errors import DecryptionError, PasswordError


class AuthenticationStore:
    """
    Authentication secrets store.

    The authentication store works in tandem with the authentication entry panels. Each
    panel contains a reference to an AuthenticationEntry object in the entry_list in the
    authentication store. In an AuthenticationEntry object, the entry_group holds the number
    used as the group in the config file holding that entry's values. sort_index controls
    the order entries appear in in the main window. The sort_index is altered as entries
    change position in the main window and just before the store is saved. The entry_group
    value is assigned when a new entry is created and doesn't change after that except
    during a regroup operation just before the store is saved.
    """

    # Current encryption algorithm name
    CURRENT_ALGORITHM = 'FERNET-256'

    @staticmethod
    def IsEncryptionActive( filename ):
        """Determine if encryption is in use for the named database."""
        cfg = wx.FileConfig( GetProgramName( ), GetVendorName( ), localFilename = filename,
                             style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        if cfg != None:
            algorithm = cfg.Read( '/crypto/algorithm', 'cleartext' )
        else:
            algorithm = 'cleartext'
        cfg = None
        return algorithm != 'cleartext'

    def __init__( self, filename, password ):
        """Initialize the store from the given filename, using a password to encrypt secrets."""
        self.cfg = wx.FileConfig( GetProgramName( ), GetVendorName( ), localFilename = filename,
                                  style = wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        self.database_filename = filename
        cfgfile = wx.FileConfig.GetLocalFileName( self.database_filename,
                                                  wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        GetLogger( ).info( "Database file: %s", cfgfile )
        self.entry_list = [ ]
        self.next_group = 1
        self.next_index = 1
        self.max_digits = 8

        # Check the encryption algorithm entry. If it's missing, the database must
        # have cleartext secrets. We'll decrypt the secrets using the old algorithm
        # and salt. Encryption will be done using the current algorithm and either
        # the existing salt (if the algorithm isn't changing) or a new salt (if the
        # algorithm has changed).
        self.algorithm = AuthenticationStore.CURRENT_ALGORITHM
        self.old_algorithm = self.cfg.Read( '/crypto/algorithm', 'cleartext' )
        oldsalt = self.cfg.Read( '/crypto/salt', '' )
        if self.old_algorithm == 'AES' or self.old_algorithm == 'cleartext':
            self.old_password_salt = oldsalt.encode( )
        else:
            self.old_password_salt = base64.urlsafe_b64decode( oldsalt.encode( ) )
        self.decryptor = create_encryption_object( self.old_algorithm, password,
                                                   self.old_password_salt )
        self.algorithm_changed = self.decryptor.algorithm != self.algorithm
        if self.algorithm_changed:
            self.password_salt = generate_salt( self.algorithm )
            self.password_changed = True
            self.encryptor = create_encryption_object( self.algorithm, password,
                                                       self.password_salt )
        else:
            self.password_salt = self.old_password_salt
            self.password_changed = False
            self.encryptor = self.decryptor

        # Read configuration entries into a list
        # Make sure to update next_group and next_index if we encounter
        #     a larger value for them than we've seen yet
        self.cfg.SetPath( '/entries' )
        more, value, index = self.cfg.GetFirstGroup( )
        while more:
            entry_group = int( value )
            ## GetLogger().debug( "AS reading group %d", entry_group )
            if entry_group > 0:
                if entry_group >= self.next_group:
                    self.next_group = entry_group + 1
                try:
                    entry = AuthenticationEntry.Load( self.cfg, entry_group, self.decryptor )
                except DecryptionError as e:
                    raise PasswordError( "Decryption failure: " + str( e ) )
                except PasswordError as e:
                    raise PasswordError( "Missing password:" + str( e ) )
                sort_index = entry.GetSortIndex( )
                ## GetLogger().debug( "AS   sort index %d", sort_index )
                if sort_index >= self.next_index:
                    self.next_index = sort_index + 1
                digits = entry.GetDigits( )
                if digits > self.max_digits:
                    self.max_digits = digits
                self.entry_list.append( entry )
            more, value, index = self.cfg.GetNextGroup( index )
        self.cfg.SetPath( '/' )
        GetLogger( ).info( "%d entries in authentication database", len( self.entry_list ) )
        GetLogger( ).debug( "AS next group %d", self.next_group )
        GetLogger( ).debug( "AS next index %d", self.next_index )

        # Force save if algorithm or password changes happened
        if self.password_changed or self.algorithm_changed:
            try:
                self.Save( True )
            except PasswordError:
                raise PasswordError( "Missing password." )

        # Make sure they're sorted at the start
        keyfunc = lambda x: x.GetSortIndex( )
        self.entry_list.sort( key = keyfunc )

    def UpdatePassword( self, password ):
        """Update the encryption password and algorithm."""
        if password == None or password == '':
            return False  # Passwordless database not allowed
        self.password_salt = generate_salt( self.algorithm )
        self.password_changed = True
        try:
            self.encryptor.SetPassword( password, salt )
        except PasswordError:
            return False
        return True

    def EntryList( self ):
        """Return the list of entries in the store."""
        return self.entry_list

    def MaxDigits( self ):
        """Return the maximum number of code digits supported."""
        return self.max_digits

    def Save( self, force = False ):
        """Save any modifications back to disk."""
        GetLogger( ).debug( "AS saving all" )
        for entry in self.entry_list:
            entry.Save( self.cfg, "/entries", self.encryptor, force )
        if self.password_changed:
            self.cfg.Write( '/crypto/salt', base64.urlsafe_b64encode( self.password_salt ) )
            self.password_changed = False
        if self.algorithm_changed:
            self.cfg.Write( '/crypto/algorithm', self.algorithm )
            # Clear out entries from old algorithms
            if self.old_algorithm == 'AES':
                self.cfg.DeleteEntry( '/crypto/check_data' )
                self.cfg.DeleteEntry( '/crypto/check_hash' )
            self.algorithm_changed = False
        self.cfg.Flush( )
        # Make sure our database of secrets is only accessible by us
        # This should be handled via SetUmask(), but it's not implemented in the Python bindings
        cfgfile = wx.FileConfig.GetLocalFileName( self.database_filename,
                                                  wx.CONFIG_USE_LOCAL_FILE | wx.CONFIG_USE_SUBDIR )
        try:
            os.chmod( cfgfile, 0o600 )
        except OSError as e:
            if e.errno != errno.ENOENT:
                GetLogger( ).warning( "Problem with database file %s", cfgfile )
                GetLogger( ).warning( "Error code %d: %s ", e.errno, e.strerror )

    def Reindex( self ):
        """
        Reindex the database.

        The entry list will be sorted and then each entry will be assigned
        a new sort index and the change saved.
        """
        GetLogger( ).debug( "AS reindexing" )
        keyfunc = lambda x: x.GetSortIndex( )
        self.entry_list.sort( key = keyfunc )
        i = 1;
        for e in self.entry_list:
            e.SetSortIndex( i )
            i += 1
        self.next_index = i
        GetLogger( ).debug( "AS next index = %d", self.next_index )
        try:
            self.Save( )
        except PasswordError:
            raise PasswordError( "Missing password." )

    def Regroup( self ):
        """
        Reindex and re-group the database.

        The current set of entries will be deleted from the database file, then
        the entry list will be sorted and new sort indexes and group numbers will
        be assigned. The new entries will be saved, resulting in a database file
        with group numbers starting from 1 again.
        """
        GetLogger( ).debug( "AS regroup" )
        keyfunc = lambda x: x.GetSortIndex( )
        self.entry_list.sort( key = keyfunc )
        self.cfg.DeleteGroup( '/entries' )
        i = 1
        for e in self.entry_list:
            e.SetGroup( i )
            e.SetSortIndex( i )
            i += 1
        self.next_group = i
        self.next_index = i
        GetLogger( ).debug( "AS next group and index = %d", i )
        try:
            self.Save( )
        except PasswordError:
            raise PasswordError( "Missing password." )

    def Add( self, provider, account, secret, digits = 6, original_label = None ):
        """
        Add a new entry to the database.

        The new entry will receive a sort index and group number one greater than the
        highest currently present in the database.
        """
        f = lambda x: x.GetProvider( ) == provider and x.GetAccount( ) == account
        elist = list( filter( f, self.entry_list ) )
        if len( elist ) > 0:
            GetLogger( ).warning( "Entry already exists for %s:%s", provider, account )
            return None
        GetLogger( ).debug( "AS adding new entry %s:%s, group %d, sort index %d",
                            provider, account, self.next_group, self.next_index )
        entry = AuthenticationEntry( self.next_group, self.next_index, provider, account, secret,
                                     digits, original_label )
        self.entry_list.append( entry )
        self.next_index += 1
        self.next_group += 1
        try:
            entry.Save( self.cfg, self )
        except PasswordError:
            raise PasswordError( "Missing password." )
        self.cfg.Flush( )
        return entry

    def Delete( self, entry_group ):
        """Delete an entry from the database."""
        GetLogger( ).debug( "AS deleting entry %d", entry_group )
        f = lambda x: x.GetGroup( ) == entry_group
        elist = list( filter( f, self.entry_list ) )
        for entry in elist:
            index = self.entry_list.index( entry )
            removed = self.entry_list.pop( index )
            GetLogger( ).debug( "AS deleted entry %d", removed.entry_group )
            self.cfg.DeleteGroup( '/entries/{0:d}'.format( removed.entry_group ) )
        self.cfg.Flush( )

    def Update( self, entry_group, provider = None, account = None, secret = None, digits = None,
                original_label = None ):
        """Update an entry in the database."""
        GetLogger( ).debug( "AS updating entry %d", entry_group )
        f = lambda x: x.GetGroup( ) == entry_group
        elist = list( filter( f, self.entry_list ) )
        if len( elist ) < 1:
            return 0  # No entry found
        if len( elist ) > 1:
            GetLogger( ).error( "AS %d duplicates of entry %d found, database likely corrupt",
                                len( elist ), entry_group )
            return -1
        entry = elist[ 0 ]
        if provider != None:
            GetLogger( ).debug( "AS new provider %s", provider )
            entry.SetProvider( provider )
        if account != None:
            GetLogger( ).debug( "AS new account %s", account )
            entry.SetAccount( account )
        if secret != None:
            GetLogger( ).debug( "AS new secret" )
            entry.SetSecret( secret )
        if digits != None:
            GetLogger( ).debug( "AS new digits %d", digits )
            entry.SetDigits( digits )
        if original_label != None:
            GetLogger( ).debug( "AS new original label %s", original_label )
            entry.SetOriginalLabel( original_label )
        ret_status = 1
        try:
            entry.Save( self.cfg, self )
        except PasswordError:
            ret_status = -100
        self.cfg.Flush( )
        return ret_status


def make_deltbl( ):
    """Make the translation table for cleaning up secrets."""
    tbl = { ord( '-' ): None }
    for c in string.whitespace:
        tbl[ ord( c ) ] = None
    return tbl


class AuthenticationEntry:
    """A single entry in the authentication store."""

    # Never changed, so just make it once
    del_tbl = make_deltbl( )

    def __init__( self, group, index, provider, account, secret, digits = 6, original_label = None ):
        """Initialize the entry."""
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
        """Compare two entries based on their entry group numbers."""
        return cmp( self.entry_group, other.entry_group ) if other != None else -1

    @classmethod
    def Load( klass, cfg, entry_group, decryptor ):
        """Create a new entry based on an entry group from the database."""
        cfgpath = '{0:d}/'.format( entry_group )
        old_path = cfg.GetPath( )
        cfg.SetPath( cfgpath )
        sort_index = cfg.ReadInt( 'sort_index' )
        provider = cfg.Read( 'provider' )
        account = cfg.Read( 'account' )
        encrypted_secret = cfg.Read( 'secret' )
        secret = decryptor.Decrypt( encrypted_secret )
        digits = cfg.ReadInt( 'digits', 6 )
        original_label = cfg.Read( 'original_label', '' )
        if original_label == '':
            original_label = provider + ':' + account
        cfg.SetPath( old_path )
        obj = klass( entry_group, sort_index, provider, account, secret,
                     digits, original_label )
        obj.modified = False  # Newly-created objects are modified, ones loaded from the database aren't
        return obj

    def Save( self, cfg, entry_group_path, encryptor, force = False ):
        """Save the entry to the database file if modified."""
        if self.modified or force:
            old_path = cfg.GetPath( )
            cfg.SetPath( entry_group_path )
            cfgpath = '{0:d}/'.format( self.entry_group )
            cfg.Write( cfgpath + 'type', 'totp' )
            cfg.WriteInt( cfgpath + 'sort_index', self.sort_index )
            cfg.Write( cfgpath + 'provider', self.provider )
            cfg.Write( cfgpath + 'account', self.account )
            cfg.Write( cfgpath + 'secret', encryptor.Encrypt( self.secret ) )
            cfg.WriteInt( cfgpath + 'digits', self.digits )
            cfg.Write( cfgpath + 'original_label', self.original_label )
            cfg.SetPath( old_path )
            self.modified = False

    def GetGroup( self ):
        """Return the entry group number."""
        return self.entry_group

    def SetGroup( self, g ):
        """Set the entry group number."""
        self.entry_group = g
        self.modified = True

    def GetSortIndex( self ):
        """Return the sort index."""
        return self.sort_index

    def SetSortIndex( self, index ):
        """Set the sort index."""
        self.sort_index = index
        self.modified = True

    def GetProvider( self ):
        """Return the provider string."""
        return self.provider

    def SetProvider( self, provider ):
        """Set the provider string."""
        self.provider = provider
        self.modified = True

    def GetAccount( self ):
        """Return the account name."""
        return self.account

    def SetAccount( self, account ):
        """Set the account name."""
        self.account = account
        self.modified = True

    def GetQualifiedAccount( self ):
        """Return the complete provider-qualified account identifier string."""
        if self.provider != '':
            qacct = self.provider + ':'
        else:
            qacct = ''
        qacct += self.account
        return qacct

    def GetDigits( self ):
        """Return the number of code digits."""
        return self.digits

    def SetDigits( self, digits ):
        """Set the number of code digits."""
        self.digits = digits
        self.modified = True

    def GetOriginalLabel( self ):
        """Return the original label text."""
        return self.original_label

    def SetOriginalLabel( self, original_label ):
        """Set the original label text."""
        self.original_label = original_label
        self.modified = True

    def GetSecret( self ):
        """Return the secret."""
        return self.secret

    def SetSecret( self, secret ):
        """
        Set the secret.

        Cleans up the secret removing any illegal characters and correcting the
        padding.
        """

        # Strip out dashes and whitespace characters that're sometimes put in the
        # text given to the user.
        self.secret = secret.translate( AuthenticationEntry.del_tbl )
        # We shouldn't need to do this, but pyotp has a problem when the
        # secret needs padding so we'll pad it ourselves which works right.
        m = len( self.secret ) % 8
        if m != 0:
            self.secret += '=' * (8 - m)
        # Need a new auth object too
        self.auth = pyotp.TOTP( self.secret )
        self.otp_problem = False
        self.modified = True

    def GetPeriod( self ):
        """Return the time period between code changes."""
        return 30  # Google Authenticator uses a 30-second period

    def GetAlgorithm( self ):
        """The hashing algorithm to use."""
        return 'SHA1'

    def GetKeyUri( self ):
        """Get the provisioning key URI."""
        uri = "otpauth://totp/" + urllib.quote( self.GetQualifiedAccount( ) )
        qs_params = { }
        qs_params[ 'secret' ] = self.secret
        if self.provider != '':
            qs_params[ 'issuer' ] = self.provider
        qs_params[ 'digits' ] = self.digits
        qs_params[ 'period' ] = self.GetPeriod( )
        qs_params[ 'algorithm' ] = self.GetAlgorithm( )
        uri += '?' + urllib.urlencode( qs_params )
        return uri

    def GenerateNextCode( self ):
        """Generate the next code in sequence from the secret."""
        if self.otp_problem:
            c = '?' * self.digits
        else:
            try:
                c = self.auth.now( )
            except Exception as e:
                c = '?' * self.digits
                self.otp_problem = True
                GetLogger( ).error( "%s:%s OTP error: %s", self.provider, self.account, unicode( e ) )
        return c
