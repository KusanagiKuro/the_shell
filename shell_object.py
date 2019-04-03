#!/usr/bin/env python3
import curses
from curses import wrapper
from os import environ


class My_Shell:
    """
    Object contains the details of the shell, including
    the environment dictionary, the local variables, etc
    """
    def __init__(self, window):
        """
        Create the shell object
        """
        self.environ = environ.copy()
        self.current_directory = self.environ["PWD"]
        self.local_variables = {}
        self.window = window
        self.window.scrollok(1)
        (self.height, self.width) = window.getmaxyx()
        self.line_length = 0
        self.prompt_length = 0
        self.cursor_pos = (0, 0)
        self.command_input = ""
        self.command_list = []
        self.command_history = []
