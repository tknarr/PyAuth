# -*- coding: utf-8 -*-

from .PyAuthApp import PyAuthApp as PyAuthApp

def main():
    app = PyAuthApp( False )
    app.MainLoop()
