#!/usr/bin/env python3
from os import chdir, getcwd
from os import environ as base_environ
from naive_lexer import get_token_list
from command_splitting import get_command_list
from exception import *
from os.path import basename, exists, isdir, isfile, abspath, join, expanduser
from readline import read_history_file, write_history_file, set_history_length
from readline import get_history_length
from subprocess import run, check_output
from sys import argv


class Shell:
    """
    Shell class that contains certain attributes of the shell as well as their
    builtin functions.
    """
    def __init__(self, environ=None):
        try:
            self.environ_dict = (base_environ.copy() if not environ
                                 else environ.copy())
            self.local_variable = self.environ_dict.copy()
            self.history_file = expanduser(".intek-shhistory.txt")
            try:
                self.history = read_history_file(self.history_file)
            except (PermissionError, FileNotFoundError):
                self.history = []
            set_history_length = 2000
            self.exit = False
            self.wait_for_execute_list = []
            self.exit_code = 0
        except TypeError:
            print("Failed to initialize Shell.")

    #################################
    #       Builtin functions       #
    #################################

    def export(self, argument_list):
        """
        Modify a variable in shell.

        Input:
            - argument_list: The arguments that have been interpreted
        """
        # If there is no other argument, stdout will be the whole list of
        # set variables.
        if len(argument_list) == 1:
            sorted_variable_name = list(self.environ_dict.keys())
            sorted_variable_name.sort()
            return "\n".join(["declare -x %s=\"%s\""
                             % (environ_variable,
                                str(self.environ_dict[environ_variable]))
                             for environ_variable in sorted_variable_name])
        # Otherwise, set the new environment variable
        for argument in argument_list[1:]:
            # If the identifier name violate the naming rule, return the error
            # message
            if re_match(r"^(=|1|2|3|4|5|6|7|8|9|0)", argument):
                return ("intek-sh: export: '%s': not a valid identifier"
                        % argument)
            # Split each arguments into a pair of name and value
            components = re_split(r"(?<!\\)=|(?<!\\)\|", str(argument), 1)
            name = components[0]
            # If the pair doesn't have value, its default value will be ""
            try:
                value = components[1]
            except IndexError:
                value = ""
            self.environ_dict[name] = value
        return ""

    def print_environment(self, argument_list):
        """
        Print out an environment variable

        Input:
            - argument_list: The arguments that have been interpreted

        Output:
            - The string represents the values of all variables, connected by
            new line character
        """
        if len(argument_list) == 1:
            return "\n".join(["%s=%s" % (key, value)
                             for key, value in self.environ_dict.items()])
        return "\n".join(self.environ_dict[argument]
                         for argument in argument_list[1:]
                         if argument in self.environ_dict)

    def unset(self, argument_list):
        """
        Remove a variable from the current environment variable dictionary

        Input:
            - argument_list: The arguments that have been interpreted
        """
        for argument in argument_list[1:]:
            if argument in self.environ_dict:
                self.environ_dict.pop(argument)
        return ""

    def exit_shell(self, argument_list):
        """
        Exit shell

        Input:
            - argument_list: Arguments interepred from user input

        Output:
            - A print message indicate whether the function runs smoothly or
            has any error.
        """
        self.exit = True
        return ("exit" +
                ("\nintek-sh: exit: Too many arguments"
                 if len(argument_list) > 2 else
                 "\nintek-sh: exit:"
                 if len(argument_list) == 2 and not argument_list[1].isdigit()
                 else ""))

    def change_dir(self, argument_list):
        """
        Change the current working directory to another directory

        Input:
            - argument_list: Arguments interepred from user input

        Output:
            - A print message indicate whether the function runs smoothly or
            has any error.
        """
        # Change the current working directory to the directory whose path is
        # the 1st argument after "cd". If there is none of them, change it to
        # the directory that is recorded as HOME variable in the environ
        try:
            new_dir = (argument_list[1] if len(argument_list) > 1
                       else self.environ_dict["HOME"])
            chdir(new_dir if not new_dir.startswith("~")
                  else expanduser(new_dir))
            self.environ_dict["PWD"] = getcwd()
            return ""
        except PermissionError:
            return self.get_error_message(new_dir, PermissionError, "cd")
        except FileNotFoundError:
            return self.get_error_message(new_dir, FileNotFoundError, "cd")
        except NotADirectoryError:
            return self.get_error_message(new_dir, NotADirectoryError, "cd")
        # When the HOME environ variable is not set, this error will raise
        except KeyError as e:
            return "intek-sh: cd: HOME not set"

    def history(self, argument_list):
        optional_argument_list = [argument for argument in argument_list
                                  if argument.startswith("-")]

    def run_builtin_command(self, argument_list, command):
        # Dictionary contains command that will run the built-in functions
        built_in_functions = {"cd": self.change_dir,
                              "exit": self.exit_shell,
                              "printenv": self.print_environment,
                              "export": self.export,
                              "unset": self.unset}
        return built_in_functions[command](argument_list)

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
            # command_list = get_command_list(token_list)
            # if not command_list:
            #    continue
            # Process arguments
            # output = shell.execute_command(argument_list)
            # print([str(item) for item in command_list])
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
