# -*- coding: utf-8 -*-
"""
Encryption for the authentication store.

Passwords and cleartext are Unicode text strings. Ciphertext is a
Unicode string containing base64-encoded data. The salt used for
key derivation is an unencoded byte string representing raw byte
data (the obsolete AES encryption method uses an unencoded or
Unicode string containing base64 data directly).
"""

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
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from fernet256 import Fernet256, InvalidToken
from Errors import DecryptionError, PasswordError


class Fernet_256:
    """
    Encryption for the authentication store.

    The token follows the format of Fernet (https://github.com/fernet/spec/blob/master/Spec.md)
    using AES256 instead of AES128 for encryption.
    """

    BLOCK_SIZE = algorithms.AES.block_size / 8

    def __init__( self, password = None, salt = None ):
        self.algorithm = 'FERNET-256'
        self.storage_key = None
        self.storage_key_salt = salt
        self.backend = default_backend( )
        if password != None and self.storage_key_salt != None:
            kdf = PBKDF2HMAC( algorithm = hashes.SHA256( ),
                              length = 64,
                              salt = self.storage_key_salt,
                              iterations = 100000,
                              backend = self.backend )
            self.storage_key = base64.urlsafe_b64encode( kdf.derive( password.encode( ) ) )

    @classmethod
    def GenerateSalt( cls ):
        """Generate an appropriate salt for key derivation."""
        return os.urandom( cls.BLOCK_SIZE )

    def SetPassword( self, new_password, new_salt = None ):
        """Derive a new storage key from a new password and optionally a new salt."""
        if new_salt != None:
            self.storage_key_salt = new_salt
        if self.storage_key_salt == None:
            raise PasswordError( "No password salt set." )
        kdf = PBKDF2HMAC( algorithm = hashes.SHA256( ),
                          length = 64,
                          salt = self.storage_key_salt,
                          iterations = 100000,
                          backend = self.backend )
        self.storage_key = base64.urlsafe_b64encode( kdf.derive( new_password ) )

    def Encrypt( self, secret ):
        """Encrypt a secret using the current key."""
        if self.storage_key == None:
            raise PasswordError( "No password set." )
        f = Fernet256( self.storage_key )
        padder = padding.PKCS7( algorithms.AES.block_size ).padder( )
        cleartext = padder.update( secret.encode( ) )
        cleartext += padder.finalize( )
        ciphertext = f.encrypt( cleartext.encode( ) )
        return unicode( ciphertext )

    def Decrypt( self, token ):
        """Decrypt a secret using the current key."""
        if self.storage_key == None:
            raise PasswordError( "No password set." )
        f = Fernet256( self.storage_key )
        try:
            cleartext = f.decrypt( token.encode( ) )
        except InvalidToken as e:
            raise DecryptionError( "Decryption failure: Invalid token: " + str( e ) )
        unpadder = padding.PKCS7( algorithms.AES.block_size ).unpadder( )
        secret = unpadder.update( cleartext )
        secret += unpadder.finalize( )
        return unicode( secret )


class Old_AES:
    """Old and insecure AES encryption."""

    BLOCK_SIZE = algorithms.AES.block_size / 8

    def __init__( self, password = None, salt = None ):
        self.algorithm = 'AES'
        self.storage_key = None
        self.storage_key_salt = salt
        self.backend = default_backend( )
        if password != None and self.storage_key_salt != None:
            kdf = PBKDF2HMAC( algorithm = hashes.SHA1( ),
                              length = 16,
                              salt = self.storage_key_salt,
                              iterations = 10000,
                              backend = self.backend )
            self.storage_key = kdf.derive( password.encode( ) )

    @classmethod
    def GenerateSalt( cls ):
        raise NotImplementedError( "Old AES does not generate a salt." )

    def SetPassword( self, new_password, new_salt = None ):
        """Derive a new storage key from a new password and optionally a new salt."""
        if new_salt != None:
            self.storage_key_salt = new_salt
        if self.storage_key_salt == None:
            raise PasswordError( "No password salt set." )
        kdf = PBKDF2HMAC( algorithm = hashes.SHA1( ),
                          length = 16,
                          salt = self.storage_key_salt,
                          iterations = 10000,
                          backend = self.backend )
        self.storage_key = kdf.derive( password )

    def Encrypt( self, cleartext ):
        """Encryption is no longer supported."""
        raise NotImplementedError( "Encryption is not supported by the legacy AES algorithm." )

    def Decrypt( self, ciphertext ):
        """Decrypt a secret using the current key."""
        if self.storage_key == None:
            raise PasswordError( "No password set." )
        try:
            b = base64.standard_b64decode( ciphertext )
            iv = b[ 0:self.BLOCK_SIZE ]
            raw_ciphertext = b[ self.BLOCK_SIZE: ]
            cipher = Cipher( algorithms.AES( self.storage_key ),
                             modes.CBC( iv ), self.backend )
            decryptor = cipher.decryptor( )
            cleartext = decryptor.update( raw_ciphertext ) + decryptor.finalize( )
        except Exception as e:
            raise DecryptionError( "Decryption failure: " + str( e ) )
        return unicode( cleartext ).rstrip( )


class Cleartext:
    """No encryption."""

    BLOCK_SIZE = 1

    def __init__( self ):
        self.algorithm = 'cleartext'

    @classmethod
    def GenerateSalt( cls ):
        raise NotImplementedError( "Cleartext does not generate a salt." )

    def SetPassword( self, new_password, new_salt = None ):
        pass

    def Encrypt( self, cleartext ):
        raise NotImplementedError( "Encryption is not supported by the cleartext algorithm." )

    def Decrypt( self, ciphertext ):
        return ciphertext


def generate_salt( algorithm_name ):
    if algorithm_name == 'FERNET-256':
        salt = Fernet_256.GenerateSalt( )
    else:
        raise NotImplementedError( "Algorithm not implemented: " + algorithm_name )
    return salt


def create_encryption_object( algorithm_name, password = None, salt = None ):
    if algorithm_name == 'FERNET-256':
        e = Fernet_256( password, salt )
    elif algorithm_name == 'AES':
        e = Old_AES( password, salt )
    elif algorithm_name == 'cleartext':
        e = Cleartext( )
    else:
        raise NotImplementedError( "Algorithm not implemented: " + algorithm_name )
    return e
