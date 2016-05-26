# -*- coding: utf-8 -*-
"""Encryption for the authentication store."""

import string
import base64
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto import Random

class AES_HMAC:
    """
    Encryption for the authentication store.

    The token follows the general format of Fernet (https://github.com/fernet/spec/blob/master/Spec.md)
    except using AES256 instead of AES128 for encryption.
    """

    def __init__( self, password ):
        self.algorithm = 'AES256-HMAC'
        self.block_size = AES.block_size
        # TODO implement

    def ChangePassword( self, new_password ):
        # TODO implement

    def Encrypt( self, cleartext ):
        # TODO implement

    def Decrypt( self, token ):
        # TODO implement

    # TODO implement


class AES_unauthenticated:
    """Old unauthenticated AES decryption."""

    def __init__( self, password ):
        self.algorithm = 'AES'
        self.block_size = AES.block_size
        # TODO implement

    def Decrypt( self, ciphertext ):
        """Decrypt a secret using the current password."""
        b = base64.standard_b64decode( ciphertext )
        iv = b[0:self.block_size]
        raw_ciphertext = b[AES.block_size:]
        cipher = AES.new( self.storage_key, AES.MODE_CBC, iv )
        cleartext = cipher.decrypt( raw_ciphertext )
        return unicode( cleartext ).rstrip()

    # TODO implement
