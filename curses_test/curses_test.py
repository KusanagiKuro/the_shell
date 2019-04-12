#!/usr/bin/env python3
import curses
import subprocess
# from re import split, match as re_split, re_match
from curses import init_pair, color_pair
from os import environ, chdir, getcwd
from os.path import basename, exists, isdir, isfile, abspath, join, expanduser
from getpass import getuser
from socket import gethostname
from os.path import relpath, abspath, expanduser


class My_Shell:
    """
    Object contains the details of the self, including
    the environment dictionary, the local variables, etc
    """

    def __init__(self, window):
        """
        Create the self object
        """
        self.environ = environ.copy()
        self.current_directory = self.environ["PWD"]
        self.local_variables = {}
        self.window = window
        self.window.scrollok(1)
        (self.height, self.width) = window.getmaxyx()
        self.line_length = 0
        self.prompt_length = 0
        self.prompt_position = 0
        self.cursor_position_in_line = 0
        self.command_input = ""
        self.command_list = []
        self.command_history = []
        self.exit = False

    def run_shell(self):
        # Setup color mode
        curses.start_color()
        curses.use_default_colors()
        # Create green and blue color pairs
        init_pair(1, curses.COLOR_GREEN, -1)
        init_pair(2, curses.COLOR_BLUE, -1)
        while not self.exit:
            # Print the prompt
            self.print_prompt()
            # Get the current line that the prompt is on
            self.prompt_position = self.window.getyx()[0]
            # Reset the cursor position value to 0
            self.cursor_position_in_line = 0
            # Get the command from user input
            self.get_new_command()
            # self.process_pipe_and_redirection()
            if not self.command_input:
                continue
            command_list = [self.command_input]
            self.print_str(command_list)
            output = []
            for command in command_list:
                output = self.execute_command(output, command)
                if self.command_input == "exit":
                    break
            self.print_str(output)

    ##########################################
    #            Command handling            #
    ##########################################

    def get_new_command(self):
        """
        Get the command input by the user and save it to the
        self object
        """
        window = self.window
        # Reset the command line's length and the current command
        self.line_length = 0
        self.command_input = ""
        # Init a new key press
        char = chr(window.getch())
        # Stop the loop when ENTER key is pressed
        while char not in ["\n"]:
            # Check if the pressed key is a character key or
            # a special key and process accordingly
            if self.check_char(char):
                self.process_character_key_press(char)
            else:
                self.process_special_key_press(char)
            # Get the new key
            char = chr(window.getch())
        # Create a new line on the self's window
        window.addstr("\n")
        self.print_str(self.command_input)
        # Add the command to the command history
        self.command_history.append(self.command_input)

    def check_char(self, char):
        """
        Check if the character is a special key or not

        Input:
            - key_press: a string represent the key being pressed

        Output:
            - True if the key pressed isn't a special or function
            key.
            - False if it is.
        """
        if ord(char) in range(32, 127):
            return True
        return False

    def process_character_key_press(self, char):
        """
        Process the character key being press

        Input:
            - self: The self object
            - char: A string represent the key being pressed
        """
        # Add the character to the self's current command
        self.command_input += char
        # Get the cursor's coordinate
        coordinate = self.window.getyx()
        max_size = self.window.getmaxyx()
        # Increase the current self line's length by 1
        self.line_length += 1
        # Print out the character on the self's window
        # If the cursor is at the end of the line, echo new character
        if (coordinate[1] == self.prompt_length + self.line_length):
            self.window.echochar(char)
        # Else, insert it at the cursor's position and move the cursor to
        # the right
        else:
            self.window.insch(char)
            self.move_cursor(coordinate[0], coordinate[1] + 1)

    def process_special_key_press(self, key_press):
        """
        Process special key being pressed

        Input:
            - self: The self object
            - key_press: The key being pressed
        """
        window = self.window
        coordinate = window.getyx()
        # Run function according to the key being pressed
        # LEFT and RIGHT arrow key will move the cursor within the line
        if key_press == chr(curses.KEY_LEFT):
            self.move_cursor(coordinate, 0, - 1)
        elif key_press == chr(curses.KEY_RIGHT):
            self.move_cursor(coordinate, 0, 1)
        # UP and DOWN key will navigate through the command history
        elif key_press == chr(curses.KEY_UP):
            pass
        elif key_press == chr(curses.KEY_DOWN):
            pass
        # BACKSPACE key deletes the 1st character on the left side
        # of the cursor
        elif key_press == chr(curses.KEY_BACKSPACE):
            self.delete_character_in_line(-1)
        # DELETE key deteles the character at the current position
        # of the cursor
        elif key_press == chr(curses.KEY_DC):
            self.delete_character_in_line()
        # HOME and END key returns the cursor to the start of the
        # command and to the end of the command respectively
        elif key_press == chr(curses.KEY_HOME):
            self.window.move(self.prompt_position,
                             self.prompt_length)
        elif key_press == chr(curses.KEY_END):
            self.window.move((self.prompt_position +
                              (self.line_length + self.prompt_length) //
                              self.width),
                             ((self.line_length + self.prompt_length) %
                              self.width))
        elif key_press == chr(curses.KEY_RESIZE):
            pass
        elif ord(key_press) == 9:
            pass
        # Adding signal handling below this.

    ##########################################
    #            Cursor movements            #
    ##########################################

    def move_cursor(self, coordinate, y, x):
        """
        Move the self's cursor to specific position

        Input:
            - self: The self object whose cursor will be moved
            - coordinate: The current coordinate of the cursor
            - y: an integer represents the movement in vertical axis
            - x: an integer represents the movement in horizontal axis
        """
        window = self.window
        if coordinate[1] + x < 0:
            window.move(coordinate[0] - 1, self.width)
        elif coordinate[1] + x > self.width:
            window.move(coordinate[0] + 1, 0)
        elif :
            window.move(coordinate[])
            window.move(y, x)
        self.cursor_position_in_line += x

    ##########################################
    #           Argument processing          #
    ##########################################

    def split_command_into_args(self, command):
        """
        Split the self command into arguments and process them to return the
        final argument list

        Input:
            - command_input: the command that user has been through piping and
            redirection process

        Output:
            - args: the list of arguments after processing globbing
            and path expandsion
        """
        args = command.split()
        # Process globbing here

        # Process path expansion here

        return args

    def execute_command(self, output, command):
        args = self.split_command_into_args(command)
        if args[0] == "cd":
            return self.change_dir(args)
        elif args[0] == "printenv":
            return self.print_environment(args)
        elif args[0] == "export":
            return self.export(args)
        elif args[0] == "unset":
            return self.unset(args)
        elif args[0] == "history":
            return self.show_history(args)
        elif args[0] == "exit":
            return self.exit_shell(args)
        else:
            return self.run_subprocess(args)

    ##########################################
    #     Builtin functions for the shell    #
    ##########################################

    def change_dir(self, args):
        try:
            new_dir = (args[1] if len(args) > 1
                       else self.environ["HOME"])
            chdir(new_dir if not new_dir.startswith("~")
                  else expanduser(new_dir))
            self.environ["PWD"] = getcwd()
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

    def export(self, args):
        """
        Set export attribute for shell variables.

        Input:
            - args: The arguments that have been interpreted
        """
        # If there is no other argument, stdout will be the whole list of
        # set variables.
        if len(args) == 1:
            sorted_variable_name = list(self.environ.keys())
            sorted_variable_name.sort()
            return "\n".join(["declare -x %s=\"%s\""
                             % (environ_variable,
                                str(self.environ[environ_variable]))
                             for environ_variable in sorted_variable_name])
        # Otherwise, set the new environment variable
        for arg in args[1:]:
            # If the identifier name violate the naming rule, return the error
            # message
            if re_match(r"^(=|1|2|3|4|5|6|7|8|9|0)", arg):
                return ("intek-sh: export: '%s': not a valid identifier" % arg)
            # Split each arguments into a pair of name and value
            components = re_split(r"(?<!\\)=|(?<!\\)\|", str(arg), 1)
            name = components[0]
            # If the pair doesn't have value, its default value will be ""
            try:
                value = components[1]
            except IndexError:
                value = ""
            self.environ[name] = value
        return ""

    def print_environment(self, args):
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
                             for key, value in self.environ.items()])
        return "\n".join(self.environ[arg]
                         for arg in args[1:]
                         if arg in self.environ)

    def unset(self, args):
        """
        Remove a variable from the current environment variable dictionary

        Input:
            - args: The arguments that have been interpreted
        """
        for arg in args[1:]:
            if arg in self.environ:
                self.environ.pop(arg)
        return ""

    def exit_shell(self, args):
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
            return subprocess.check_output(args, env=self.environ,
                                           universal_newlines=True)[:-1]
        except IsADirectoryError:
            return get_error_message(args[0], IsADirectoryError)
        except PermissionError:
            return get_error_message(args[0], PermissionError)
        except subprocess.CalledProcessError:
            return ""

    def exit(self, args):
        # Add the command history into the file first before exiting
        self.exit = True
        return ("exit" +
                ("\nintek-sh: exit: Too many arguments"
                 if len(args) > 2 else
                 "\nintek-sh: exit:"
                 if len(args) == 2 and not args[1].isdigit()
                 else ""))

    ##########################################
    #     Utility functions for the shell    #
    ##########################################

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
                            for bin_dir in self.environ["PATH"].split(":")
                            ])
            except KeyError:
                return False

    def print_prompt(self):
        """
        Print the prompt in this format:
        {username}@{hostname}:{relative path of current directory from home}

        Input:
            - self: the self object
        """
        # Get the current coordinate of the cursor
        coordinate = self.window.getyx()
        # Get the username
        user = getuser()
        # Get the relative path from the HOME directory to the current
        # directory
        current_dir = self.environ["PWD"].replace(self.environ["HOME"], "~")
        # Get the host name
        hostname = gethostname()
        # Print out the prompt on the self window
        self.window.addstr("%s" % user,
                           curses.A_BOLD | color_pair(1))
        self.window.addstr("@%s" % hostname,
                           curses.A_BOLD | color_pair(1))
        self.window.addstr(":")
        self.window.addstr("%s" % current_dir,
                           curses.A_BOLD | color_pair(2))
        self.window.addstr("$ ")
        # Set the prompt length of the self
        self.prompt_length = (coordinate[1] +
                              len(user + hostname + current_dir) +
                              4)

    def print_str(self, object, end="\n"):
        """
        Act like builtin function print but on curses window

        Input:
            - object: Any object that can be converted into string
            - end: a string that will be added after the object is printed
        """
        self.window.addstr(str(object) + end)

    def delete_character_in_line(self, coordinate, position=0):
        """
        Delete the character at certain coordinate in line,
        as well as remove it from the current command

        Input:
            - coordinate: The cursor's current coordinate
            - position: position of the character that will be removed.
            This will be relative to the cursor's current coordinate.
            The value of -1 will be the previous character, while 0 is the
            character that the cursor is on.
        """
        # Delete the character
        if coordinate[1] + position < 0:
            self.window.delch(coordinate[0] - 1, self.width)
        else:
            self.window.delch(coordinate[0], coordinate[1] + position)
        # Reduce the command line length
        self.line_length -= 1
        # Move the cursor
        if position:
            self.move_cursor(coordinate, 0, position)
        # Remove the character from the current command
        self.command_input = (self.command_input[:x-self.prompt_length] +
                              self.command_input[x-self.prompt_length+1:])
