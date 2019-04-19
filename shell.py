#!/usr/bin/env python3
from os import environ as base_environ
from os import chdir, getcwd
from os.path import basename, exists, isdir, isfile, abspath, join, expanduser
from readline import read_history_file, write_history_file, set_history_length
from readline import get_history_length


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
