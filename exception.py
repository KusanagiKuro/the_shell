#!/usr/bin/env python3
class Error(Exception):
    pass


class BadSubstitutionError(Error):
    def __init__(self, argument):
        self.argument = argument
