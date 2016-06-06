# -*- coding: utf-8 -*-
"""Encryption for the authentication store."""

import string
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from fernet256 import Fernet256

class Fernet_256:
    """
    Encryption for the authentication store.

    The token follows the format of Fernet (https://github.com/fernet/spec/blob/master/Spec.md)
    using AES256 instead of AES128 for encryption.
    """

    def __init__( self, password = None, salt = None ):
        self.algorithm = 'FERNET-256'
        self.block_size = algorithms.AES.block_size / 8
        self.storage_key = None
        self.storage_key_salt = salt
        self.backend = default_backend()
        if password != None and self.storage_key_salt != None:
            kdf = PBKDF2HMAC( algorithm = hashes.SHA256(),
                              length = 64,
                              salt = self.storage_key_salt,
                              iterations = 100000,
                              backend = self.backend )
            self.storage_key = base64.urlsafe_b64encode( kdf.derive( password ) )

    def SetPassword( self, new_password, new_salt = None ):
        """Derive a new storage key from a new password and optionally a new salt."""
        if new_salt != None:
            self.storage_key_salt = new_salt
        if self.storage_key_salt == None:
            raise ValueError( "No password salt set." )
        kdf = PBKDF2HMAC( algorithm = hashes.SHA256(),
                          length = 64,
                          salt = self.storage_key_salt,
                          iterations = 100000,
                          backend = self.backend )
        self.storage_key = base64.urlsafe_b64encode( kdf.derive( new_password ) )

    def Encrypt( self, secret ):
        """Encrypt a secret using the current key."""
        if self.storage_key == None:
            raise ValueError( "No password set." )
        f = Fernet256( self.storage_key )
        padder = padding.PKCS7( algorithms.AES.block_size ).padder()
        cleartext = padder.update( secret )
        cleartext += padder.finalize()
        ciphertext = f.encrypt( cleartext )
        return unicode( ciphertext )

    def Decrypt( self, token ):
        """Decrypt a secret using the current key."""
        if self.storage_key == None:
            raise ValueError( "No password set." )
        f = Fernet256( self.storage_key )
        cleartext = f.decrypt( token )
        unpadder = padding.PKCS7( algorithms.AES.block_size ).unpadder()
        secret = unpadder.update( cleartext )
        secret += unpadder.finalize()
        return unicode( secret )


class Old_AES:
    """Old and insecure AES encryption."""

    def __init__( self, password = None, salt = None ):
        self.algorithm = 'AES'
        self.block_size = algorithms.AES.block_size / 8
        self.storage_key = None
        self.storage_key_salt = salt
        self.backend = default_backend()
        if password != None and self.storage_key_salt != None:
            kdf = PBKDF2HMAC( algorithm = hashes.SHA1(),
                              length = self.block_size,
                              salt = self.storage_key_salt,
                              iterations = 10000,
                              backend = self.backend )
            self.storage_key = base64.b64encode( kdf.derive( password ) )

    def SetPassword( self, new_password, new_salt = None ):
        """Derive a new storage key from a new password and optionally a new salt."""
        if new_salt != None:
            self.storage_key_salt = new_salt
        if self.storage_key_salt == None:
            raise ValueError( "No password salt set." )
        kdf = PBKDF2HMAC( algorithm = hashes.SHA1(),
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
            raise ValueError( "No password set." )
        b = base64.standard_b64decode( ciphertext )
        iv = b[0:self.block_size]
        raw_ciphertext = b[self.block_size:]
        cipher = Cipher( algorithms.AES( base64.b64decode( self.storage_key ) ),
                         modes.CBC( iv ), self.backend )
        decryptor = cipher.decryptor()
        cleartext = decryptor.update( raw_ciphertext ) + decryptor.finalize()
        return unicode( cleartext ).rstrip()
