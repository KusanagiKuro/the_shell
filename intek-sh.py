#!/usr/bin/env python3
from naive_lexer import get_token_list
from command_splitting import get_command_list
from token_expansion import expand_token_for_command_list
from shell import Shell
from exception import *
from sys import argv


#################################
#      Subprocess Handling      #
#################################


def run_subprocess(self, argument_list):
    """
    Input:
    - argument_list: Arguments interepred from user input

    Output:
    - A print message indicate whether the function runs smoothly or
    has any error.
    """
    if not self.is_command_exist(argument_list):
        return (("intek-sh: %s: No such file or directory"
                 % argument_list[0])
                if argument_list[0].startswith("./")
                else "intek-sh: %s: command not found" % argument_list[0])
    try:
        return subprocess.check_output(argument_list,
                                       env=self.environ_dict,
                                       universal_newlines=True)[:-1]
    except IsADirectoryError:
        return self.get_error_message(argument_list[0], IsADirectoryError)
    except PermissionError:
        return self.get_error_message(argument_list[0], PermissionError)
    except subprocess.CalledProcessError:
        return ""

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


def get_error_message(self, argument, error, command_name=None):
    return ""


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
    while not shell.exit:
        try:
            # Read user input
            user_input = read_user_input()
            token_list = get_token_list(user_input)
            print("\n".join([str(item) for item in token_list]))
            # print("".join([item.original_string for item in token_list]))
            command_list = get_command_list(token_list)
            if not command_list:
                continue
            expand_token_for_command_list(command_list, shell)
            print([item.argument_string for item in command_list])
        except EOFError:
            return
        except BadSubstitutionError as e:
            print("intek-sh: %s: bad substitution" % e.argument)
        except UnexpectedTokenError as e:
            print("intek-sh: Unexpected token after %s" % e.argument)
        except CommandNotFoundError as e:
            print("intek-sh: %s: command not found" % e.argument)


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
