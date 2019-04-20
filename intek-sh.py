#!/usr/bin/env python3
from naive_lexer import get_token_list
from command_splitting import get_command_list
from token_expansion import expand_token_for_command_list
from readline import get_history_item, get_current_history_length,\
                     add_history, set_history_length, read_history_file,\
                     remove_history_item
from os.path import isfile, join, expanduser
from shell import Shell
from exception import BadSubstitutionError, UnexpectedTokenError,\
                      CommandNotFoundError, EventNotFoundError
from utility import get_error_message, get_history_log
from sys import argv


#################################
#       Utility functions       #
#################################


def is_command_exist(self, argument_list):
    """
    Check if the command exist

    Input:
        - argument_list: Arguments interepred from user input,
        its first element is the command

    Output:
        - True if the command exists in PATH (or current directory if the
        command contains ./)
        - False otherwise
    """
    # If the command called is a script, check it in the current file
    if (argument_list[0].startswith(".") or
            argument_list[0].startswith("..") or
            argument_list[0].startswith("~")):
        return isfile(argument_list[0])
    # Else, check it in each directory in the PATH environment
    else:
        try:
            return any([isfile(join(bin_dir, argument_list[0]))
                        for bin_dir in self.environ_dict["PATH"].split(":")
                        ])
        except KeyError:
            return False


#################################
#         Input Handling        #
#################################


def read_user_input():
    """
    Allow the user to type in the input

    Output:
        - The user's input
    """
    return input("intek-sh$ ")


#################################
#         Run function          #
#################################


def run(shell):
    """
    Run the shell until the exit command is called

    Input:
        - shell: a shell object that will be run
    """
    set_history_length(2000)
    try:
        read_history_file(Shell.history_file)
    except FileNotFoundError:
        open(Shell.history_file, "w+").close()
    except PermissionError:
        pass
    while not shell.exit:
        try:
            # Read user input
            user_input = read_user_input()
            if user_input:
                remove_history_item(get_current_history_length() - 1)
            else:
                continue
            token_list, list_of_char = get_token_list(user_input)
            # Add final input string after get_history_item
            input_string = "".join(list_of_char)
            if (get_history_item(get_current_history_length()) != input_string
                    and input_string):
                add_history(input_string)
            print(" ".join([str(item) for item in token_list]))
            # print("\n".join([str(item) for item in token_list]))
            # print("".join([item.original_string for item in token_list]))
            command_list = get_command_list(token_list)
            if not command_list:
                continue
            expand_token_for_command_list(command_list, shell)
            # print(command_list)
            # print([item.argument_list for item in command_list])
        except EOFError:
            return
        except BadSubstitutionError as e:
            print("intek-sh: %s: bad substitution" % e.argument)
        except UnexpectedTokenError as e:
            print("intek-sh: Unexpected token after %s" % e.argument)
        except CommandNotFoundError as e:
            print("intek-sh: %s: command not found" % e.argument)
        except EventNotFoundError as e:
            print("intek-sh: %s: event not found" % e.argument)


def main():
    try:
        shell = Shell()
        if "-sub" in argv:
            run_subshell(shell, argv)
        else:
            run(shell)
    except TypeError:
        return


if __name__ == "__main__":
    main()
