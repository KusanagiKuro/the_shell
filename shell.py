#!/usr/bin/env python3
from os import environ as base_environ
from os import chdir, getcwd
from os.path import basename, exists, isdir, isfile, abspath, join, expanduser
from readline import read_history_file, write_history_file, set_history_length,\
                     get_history_length, get_history_item
from utility import get_error_message, get_history_log
from sys import exit as system_exit


class Shell:
    """
    Shell class that contains certain attributes of the shell as well as their
    builtin functions.
    """
    history_file = expanduser("~/.intek-shhistory.txt")

    def __init__(self, environ=None):
        try:
            self.environ_dict = (base_environ.copy() if not environ
                                 else environ.copy())
            self.local_variable = self.environ_dict.copy()
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
        exit_code = 0
        # If there is no other argument, stdout will be the whole list of
        # set variables.
        if len(argument_list) == 1:
            sorted_variable_name = list(self.environ_dict.keys())
            sorted_variable_name.sort()
            print("\n".join(["declare -x %s=\"%s\""
                             % (environ_variable,
                                str(self.environ_dict[environ_variable]))
                             for environ_variable in sorted_variable_name]))
            return 0
        for argument in argument_list:
            
        return exit_code

    def print_environment(self, argument_list):
        """
        Print out an environment variable

        Input:
            - argument_list: The arguments that have been interpreted

        Output:
            - The string represents the values of all variables, connected by
            new line character
        """
        exit_code = 0
        for argument in argument_list:
            if argument in self.environ_dict.keys():
                print(self.environ_dict)
        if len(argument_list) == 1:
            print("\n".join(["%s=%s" % (key, value)
                             for key, value in self.environ_dict.items()]))
        else:
            print("\n".join(self.environ_dict[argument]
                            for argument in argument_list[1:]
                            if argument in self.environ_dict))
        return exit_code

    def unset(self, argument_list):
        """
        Remove a variable from the current environment variable dictionary

        Input:
            - argument_list: The arguments that have been interpreted
        """
        for argument in argument_list[1:]:
            if argument in self.environ_dict:
                self.environ_dict.pop(argument)
        return 0

    def exit_shell(self, argument_list):
        """
        Exit shell

        Input:
            - argument_list: Arguments interepred from user input

        Output:
            - A print message indicate whether the function runs smoothly or
            has any error.
        """
        print("exit")
        try:
            exit_code = int(argument_list[1])
        except ValueError:
            print("intek-sh: exit: numeric argument required")
            system_exit(2)
        except IndexError:
            system_exit(0)
        if len(argument_list) > 2:
            print("intek-sh: exit: Too many arguments")
        system_exit(exit_code % 256)


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
            return get_error_message(new_dir, PermissionError, "cd")
        except FileNotFoundError:
            return get_error_message(new_dir, FileNotFoundError, "cd")
        except NotADirectoryError:
            return get_error_message(new_dir, NotADirectoryError, "cd")
        # When the HOME environ variable is not set, this error will raise
        except KeyError:
            return "intek-sh: cd: HOME not set"

    def execute_history_command(self, argument_list):
        try:
            if len(argument_list) > 2:
                print("intek-sh: history: too many arguments")
                return 1
            elif len(argument_list) == 2:
                number = int(argument_list[1])
                self.print_history(number)
                return 0
            else:
                self.print_history()
                return 0
        except ValueError:
            print("history requires a numeric argument")
            return 1
    
    def print_history(self, number=1000):
        if number > 1000:
            number = 1000
        history_log = get_history_log()
        converted_history_log = [
            "{0:>5} {1}".format(index, command)
            for index, command in enumerate(history_log)
        ]
        if len(history_log) < number:
            print("\n".join(converted_history_log))
        else:
            print("\n".join(converted_history_log[-number:]))


    def run_builtin_command(self, argument_list, command):
        # Dictionary contains command that will run the built-in functions
        built_in_functions = {"cd": self.change_dir,
                              "exit": self.exit_shell,
                              "printenv": self.print_environment,
                              "export": self.export,
                              "unset": self.unset,
                              "history": self.execute_history_command}
        return built_in_functions[command](argument_list)
