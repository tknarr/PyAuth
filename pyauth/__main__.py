# -*- coding: utf-8 -*-

import sys
from .PyAuthApp import PyAuthApp as PyAuthApp


def main():
    app = PyAuthApp( False )
    app.MainLoop()
