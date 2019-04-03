#!/usr/bin/env python3
import curses
from curses import wrapper, init_pair, color_pair
from os import environ
from os.path import relpath, abspath
from getpass import getuser
from socket import gethostname
from shell_object import My_Shell


def run_shell(new_window):
    """
    Run the shell

    Input:
        - new_window: the window that the shell will be using as its place to
        print out stdout, stderr and take in stdin
    """
    curses_setup()
    # Create the new shell object with the window passed to
    # the function
    shell = My_Shell(new_window)
    # Getting input and execute the command
    while True:
        # Print the prompt
        print_prompt(shell)
        # Get the command from user input
        get_new_command(shell)
        # process_pipe_and_redirection(shell)
        argument_list = split_command_into_args(shell)
        if shell.command_input == "exit":
            break


def curses_setup():
    """
    Setup the curses module color, mode, etc before running the shell
    """
    # Setup color mode
    curses.start_color()
    curses.use_default_colors()
    # Create green and blue color pairs
    init_pair(1, curses.COLOR_GREEN, -1)
    init_pair(2, curses.COLOR_BLUE, -1)


def print_prompt(shell):
    """
    Print the prompt in this format:
    {username}@{hostname}:{relative path of current directory from home}

    Input:
        - shell: the shell object
    """
    # Get the current coordinate of the cursor
    coordinate = shell.window.getyx()
    # Get the username
    user = getuser()
    # Get the relative path from the HOME directory to the current
    # directory
    current_dir = shell.environ["PWD"].replace(shell.environ["HOME"], "~")
    # Get the host name
    hostname = gethostname()
    # Print out the prompt on the shell window
    shell.window.addstr("%s" % user,
                        curses.A_BOLD | color_pair(1))
    shell.window.addstr("@%s" % hostname,
                        curses.A_BOLD | color_pair(1))
    shell.window.addstr(":")
    shell.window.addstr("%s" % current_dir,
                        curses.A_BOLD | color_pair(2))
    shell.window.addstr("$ ")
    # Set the prompt length of the shell
    shell.prompt_length = (coordinate[1] +
                           len(user + hostname + current_dir) +
                           4)


def get_new_command(shell):
    """
    Get the command input by the user and save it to the
    shell object

    Input:
        - shell: The shell object
    """
    window = shell.window
    # Reset the command line's length and the current command
    shell.line_length = 0
    shell.command_input = ""
    # Init a new key press
    char = chr(window.getch())
    # Stop the loop when ENTER key is pressed
    while char not in ["\n"]:
        # Check if the pressed key is a character key or
        # a special key and process accordingly
        if check_key(char):
            process_character_key_press(shell, char)
        else:
            process_special_key_press(shell, char)
        # Get the new key
        char = chr(window.getch())
    # Create a new line on the shell's window
    window.addstr("\n")
    # Add the command to the command history
    shell.command_history.append(shell.command_input)


def check_key(char):
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


def process_character_key_press(shell, char):
    """
    Process the character key being press

    Input:
        - shell: The shell object
        - char: A string represent the key being pressed
    """
    # Add the character to the shell's current command
    shell.command_input += char
    # Get the cursor's coordinate
    coordinate = shell.window.getyx()
    max_size = shell.window.getmaxyx()
    # Print out the character on the shell's window
    # If the cursor is at the end of the line, echo new character
    if (coordinate[1] == shell.prompt_length + shell.line_length):
        shell.window.echochar(char)
    # Else, insert it at the cursor's position and move the cursor to
    # the right
    else:
        shell.window.insch(char)
        move_cursor_in_line(shell, coordinate[0], coordinate[1] + 1)
    # Increase the current shell line's length by 1
    shell.line_length += 1


def process_special_key_press(shell, key_press):
    """
    Process special key being pressed

    Input:
        - shell: The shell object
        - key_press: The key being pressed
    """
    window = shell.window
    coordinate = window.getyx()
    # Run function according to the key being pressed
    # LEFT and RIGHT arrow key will move the cursor within the line
    if key_press == chr(curses.KEY_LEFT):
        move_cursor_in_line(shell, coordinate[0], coordinate[1] - 1)
    elif key_press == chr(curses.KEY_RIGHT):
        move_cursor_in_line(shell, coordinate[0], coordinate[1] + 1)
    # UP and DOWN key will navigate through the command history
    elif key_press == chr(curses.KEY_UP):
        pass
    elif key_press == chr(curses.KEY_DOWN):
        pass
    # BACKSPACE key deletes the 1st character on the left side
    # of the cursor
    elif key_press == chr(curses.KEY_BACKSPACE):
        if coordinate[1] > shell.prompt_length:
            delete_character_in_line(shell, coordinate[0],
                                     coordinate[1] - 1)
    # DELETE key deteles the character at the current position
    # of the cursor
    elif key_press == chr(curses.KEY_DC):
        if (shell.prompt_length + shell.line_length >
                coordinate[1] >
                shell.prompt_length - 1):
            delete_character_in_line(shell, coordinate[0],
                                     coordinate[1])
    # HOME and END key returns the cursor to the start of the
    # command and to the end of the command respectively
    elif key_press == chr(curses.KEY_HOME):
        move_cursor_in_line(shell, coordinate[0],
                            shell.prompt_length)
    elif key_press == chr(curses.KEY_END):
        move_cursor_in_line(shell, coordinate[0],
                            shell.prompt_length + shell.line_length)
    elif key_press == chr(curses.KEY_RESIZE):
        pass
    elif ord(key_press) == 9:
        pass


def move_cursor_in_line(shell, y, x):
    """
    Move the shell's cursor to specific position

    Input:
        - shell: The shell object whose cursor will be moved
        - y: an integer represents the new y coordinate
        - x: an integer represents the new x coordinate
    """
    window = shell.window
    # If the new x coordinate is within the command line, move the cursor
    if x in range(shell.prompt_length,
                  shell.prompt_length + shell.line_length + 1):
        window.move(y, x)


def delete_character_in_line(shell, y, x):
    """
    Delete the character at certain coordinate in line,
    as well as remove it from the current command

    Input:
        - shell: The shell object
        - y: an integer represents the y coordinate of the character
        that will be removed
        - x: an integer represents the x coordinate of the character
        that will be removed
    """
    # Delete the character
    shell.window.delch(y, x)
    # Reduce the command line length
    shell.line_length -= 1
    # Move the cursor
    move_cursor_in_line(shell, y, x)
    # Remove the character from the current command
    shell.command_input = (shell.command_input[:x - shell.prompt_length] +
                           shell.command_input[x - shell.prompt_length + 1:])


def print_str(window, string, end="\n"):
    """
    Act like builtin function print but on curses window

    Input:
        - shell: The shell object whose curses window will be printed on
        - string: The string that will be printed on the window
    """
    shell.window.addstr(string + end)


def split_command_into_args(command_input):
    """
    Split the shell command into arguments and process them to return the final
    argument list

    Input:
        - command_input: the command that user has been through piping and
        redirection process

    Output:
        - argument_list: the list of arguments after processing globbing and
        path expandsion
    """
    argument_list = shell.command_input.split()
    process_globbing(argument_list)
    process_path_expansions(argument_list)
    return argument_list


def process_globbing(argument_list):
    pass


def process_path_expansions(argument_list):
    pass


if __name__ == "__main__":
    wrapper(run_shell)
