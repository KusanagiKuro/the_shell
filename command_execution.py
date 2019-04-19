#!/usr/bin/env python3
from token_definition import *
from subprocess import Popen
from token_expansion import *


def execute_single_command(command,
                           shell,
                           print=False):
    command_string = ""
    if any(isinstance(token, Subshell_Token)):
        return execute_subshell(token, shell)
    for token in command.token_list:
        command_string += expand_token(token, shell)
    pass


def execute_pipe_command(command,
                         shell,
                         print=False):
    pass


def execute_and_command(command,
                        shell,
                        print=False):
    pass


def execute_or_command(command,
                       shell,
                       print=False):
    pass


def execute_command(command,
                    shell,
                    print=False):
    if isinstance(command, Command):
        execute_single_command(command,
                               shell)
    elif isinstance(command, Pipe_Command):
        execute_pipe_command(command,
                             shell)
    elif isinstance(command, And_Command):
        execute_and_command(command,
                            shell)
    elif isinstance(command, Or_Command):
        execute_or_command(command,
                           shell)
    else:
        print("command parameter for execute_command function",
              "requires a Command type or Binary type object")


def execute_command_list(command,
                         shell):
    for command in command_list:
        execute_command(
            command,
            shell
        )
