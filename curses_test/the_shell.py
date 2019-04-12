#!/usr/bin/env python3
import curses
from curses import wrapper
from shell_object import My_Shell


def run_shell(new_window):
    """
    Run the shell

    Input:
        - new_window: the window that the shell will be using as its place to
        print out stdout, stderr and take in stdin
    """
    # Create the new shell object with the window passed to
    # the function
    shell = My_Shell(new_window)
    shell.run_shell()


if __name__ == "__main__":
    wrapper(run_shell)
