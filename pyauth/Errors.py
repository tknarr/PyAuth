# -*- coding: utf-8 -*-
"""Exceptions used by other modules."""

class AuthenticationError( RuntimeError ):
    pass

class PasswordError( RuntimeError ):
    pass

class DecryptionError( RuntimeError ):
    pass
