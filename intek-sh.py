#!/usr/bin/env python3
from os import chdir, getcwd
from os import environ as base_environ
from os.path import basename, exists, isdir, isfile, abspath, join, expanduser
from readline import read_history_file, write_history_file, set_history_length
from readline import get_history_length
from re import split as re_split
from re import match as re_match
import subprocess


class Shell:
    def __init__(self, environ=None):
        try:
            self.environ_dict = (base_environ.copy() if not environ
                                 else environ.copy())

            self.history_file = expanduser(".intek-sh_history.txt")
            readline.set_history_length = 2000
            self.exit = False
            self.wait_for_execute_list = []
        except TypeError:
            print("Failed to initialize Shell.")

    #################################
    #         Input Handling        #
    #################################

    def read_user_input(self):
        """
        Allow the user to type in the input

        Output:
            - The user's input
        """
        return input("intek-sh$ ")

    def process_pipes_redirections(self, user_input):
        """
        Simple interpreter for the user's input

        Input:
            - user_input: The user's input

        Output:
            - The arguments that are interpreted from the user's input
        """
        if not user_input:
            return None
        # args_list = re_split(r"(?<!\\)>", user_input)
        args_list = user_input
        return args_list

    def process_logical_operator(self, user_input):
        return user_input

    def argument_handling(self, user_input):
        args = self.split_input_by_double_quotes(user_input)
        args = self.replace_command_substitutions(args)
        args = self.replace_path_expansion(args)
        return args

    def process_arguments(self, argument_list):
        # Insert globbing

        # Insert path expansion and parameter expansion

        return argument_list

    def execute_command(self, args, output=None):
        """
        Execute the command

        Input:
            - command: The command needs to be executed
            - output: The previous command's stdout

        Output:
            - The stdout after the command has been run
        """
        # If there is output from previous command, add it to the current
        # command's arguments
        if output:
            args.append(output)
        # Dictionary contains command that will run the built-in functions
        built_in_functions = {"cd": self._change_dir,
                              "exit": self._exit_shell,
                              "printenv": self._print_environment,
                              "export": self._export,
                              "unset": self._unset}
        return (built_in_functions.get(args[0], self.run_subprocess)(args))

    #################################
    #       Builtin functions       #
    #################################

    def _export(self, args):
        """
        Set _export attribute for shell variables.

        Input:
            - args: The arguments that have been interpreted
        """
        # If there is no other argument, stdout will be the whole list of
        # set variables.
        if len(args) == 1:
            sorted_variable_name = list(self.environ_dict.keys())
            sorted_variable_name.sort()
            return "\n".join(["declare -x %s=\"%s\""
                             % (environ_variable,
                                str(self.environ_dict[environ_variable]))
                             for environ_variable in sorted_variable_name])
        # Otherwise, set the new environment variable
        for arg in args[1:]:
            # If the identifier name violate the naming rule, return the error
            # message
            if re_match(r"^(=|1|2|3|4|5|6|7|8|9|0)", arg):
                return ("intek-sh: _export: '%s': not a valid identifier"
                        % arg)
            # Split each arguments into a pair of name and value
            components = re_split(r"(?<!\\)=|(?<!\\)\|", str(arg), 1)
            name = components[0]
            # If the pair doesn't have value, its default value will be ""
            try:
                value = components[1]
            except IndexError:
                value = ""
            self.environ_dict[name] = value
        return ""

    def _print_environment(self, args):
        """
        Print out an environment variable

        Input:
            - args: The arguments that have been interpreted

        Output:
            - The string represents the values of all variables, connected by
            new line character
        """
        if len(args) == 1:
            return "\n".join(["%s=%s" % (key, value)
                             for key, value in self.environ_dict.items()])
        return "\n".join(self.environ_dict[arg]
                         for arg in args[1:]
                         if arg in self.environ_dict)

    def _unset(self, args):
        """
        Remove a variable from the current environment variable dictionary

        Input:
            - args: The arguments that have been interpreted
        """
        for arg in args[1:]:
            if arg in self.environ_dict:
                self.environ_dict.pop(arg)
        return ""

    def _exit_shell(self, args):
        """
        Exit shell

        Input:
            - args: Arguments interepred from user input

        Output:
            - A print message indicate whether the function runs smoothly or
            has any error.
        """
        self.exit = True
        return ("exit" +
                ("\nintek-sh: exit: Too many arguments"
                 if len(args) > 2 else
                 "\nintek-sh: exit:"
                 if len(args) == 2 and not args[1].isdigit()
                 else ""))

    def _change_dir(self, args):
        """
        Change the current working directory to another directory

        Input:
            - args: Arguments interepred from user input

        Output:
            - A print message indicate whether the function runs smoothly or
            has any error.
        """
        # Change the current working directory to the directory whose path is
        # the 1st argument after "cd". If there is none of them, change it to
        # the directory that is recorded as HOME variable in the environ
        try:
            new_dir = args[1] if len(args) > 1 else self.environ_dict["HOME"]
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

    #################################
    #      Subprocess Handling      #
    #################################

    def run_subprocess(self, args):
        """
        Exit shell (incomplete)

        Input:
        - args: Arguments interepred from user input

        Output:
        - A print message indicate whether the function runs smoothly or
        has any error.
        """
        if not self.is_command_exist(args):
            return ("intek-sh: %s: No such file or directory" % args[0]
                    if args[0].startswith("./")
                    else "intek-sh: %s: command not found" % args[0])
        try:
            return subprocess.check_output(args, env=self.environ_dict,
                                           universal_newlines=True)[:-1]
        except IsADirectoryError:
            return self.get_error_message(args[0], IsADirectoryError)
        except PermissionError:
            return self.get_error_message(args[0], PermissionError)
        except subprocess.CalledProcessError:
            return ""

    #################################
    #       Utility functions       #
    #################################

    def is_command_exist(self, args):
        """
        Check if the command exist

        Input:
            - args: Arguments interepred from user input, its first element is
            the command

        Output:
            - True if the command exists in PATH (or current directory if the
            command contains ./)
            - False otherwise
        """
        # If the command called is a script, check it in the current file
        if (args[0].startswith(".") or args[0].startswith("..") or
                args[0].startswith("~")):
            return isfile(args[0])
        # Else, check it in each directory in the PATH environment
        else:
            try:
                return any([isfile(join(bin_dir, args[0]))
                            for bin_dir in self.environ_dict["PATH"].split(":")
                            ])
            except KeyError:
                return False

    def get_error_message(self, argument, error, command_name=None):
        return ""

    #################################
    #         Run function         #
    #################################

    def run(self):
        """
        Run the shell until the exit command is called
        """
        while not self.exit:
            try:
                # Read user input
                user_input = self.read_user_input()
                argument_list = user_input.split()
                argument_list = self.process_arguments(argument_list)
                output = self.execute_command(args)
                print(output)
                # command_list = self.process_logical_operator(user_input)
                # Interpret that input
                # command_list = self.process_pipes_redirections(user_input)
                # if command_list:
                #     output = None
                #     # Run each command separately, the output of previous
                #     # command will be the input of the next one
                #     for command in command_list:
                #         output = self.execute_command(command, output)
                #     # Print out the final stdout
                #     print(output + "\n" if output else "", end="")
            except EOFError:
                return


def main():
    try:
        shell = Shell()
        shell.run()
    except TypeError:
        return


if __name__ == "__main__":
    main()
