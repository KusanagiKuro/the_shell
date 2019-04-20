#!/usr/bin/env python3
from token_definition import Subshell_Token, Command, Binary_Command,\
                             Pipe_Command, And_Command, Or_Command
from token_expansion import expand_token, find_next_element_of_type_in_list
from subprocess import Popen


def execute_single_command(command,
                           shell,
                           print=False):
    if any([isinstance(token, Subshell_Token)
            for token in command.token_list]):
        token = find_next_element_of_type_in_list(command.token_list,
                                                  Subshell_Token)
        return execute_subshell(token, shell)


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


def execute_subshell(token, shell):
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


def execute_command_list(command_list,
                         shell):
    for command in command_list:
        execute_command(
            command,
            shell
        )
