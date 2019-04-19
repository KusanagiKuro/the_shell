#!/usr/bin/env python3
class Error(Exception):
    pass


class BadSubstitutionError(Error):
    def __init__(self, argument):
        self.argument = argument


class UnexpectedTokenError(Error):
    def __init__(self, argument):
        self.argument = argument


class CommandNotFoundError(Error):
    def __init__(self, argument):
        self.argument = argument
