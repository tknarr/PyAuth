# -*- coding: utf-8 -*-
"""Main routine if invoking directly without use of a wrapper script."""

from PyAuthApp import PyAuthApp as PyAuthApp

def main():
    app = PyAuthApp( False )
    app.MainLoop()
