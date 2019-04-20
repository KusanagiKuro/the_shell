#!/usr/bin/env python3
from token_definition import Operator_Token, Word_Token, Param_Expand_Token,\
                             Double_Quote_Token, Single_Quote_Token, Subshell_Token,\
                             Command, Or_Command, And_Command, Pipe_Command,\
                             Binary_Command, Token, Separator_Token
from exception import UnexpectedTokenError
from naive_lexer import get_token_list


##############################
#      Special Operators     #
##############################


def process_special_operator(token,
                             token_list,
                             binary_command,
                             command_list):
    """
    Process special operator and return a binary command accordingly

    Input:
        - token: the logical operator token that has been captured
        - token_list: the current tokens that have been captured
        - binary_command: the current unfinished binary command
        - command_list: the command list that will be returned to the user
        after all tokens have been processed

    Output:
        - binary_command: the final unfinished binary command after processing
    """
    # If the operator is a logical operator, return the result after processing
    # logical operator
    if token.content != ";":
        return process_logical_operator(token,
                                        token_list,
                                        binary_command)
    # Else return the result after processing semicolon
    else:
        return process_semicolon_operator(token,
                                          token_list,
                                          binary_command,
                                          command_list)


def process_logical_operator(token,
                             token_list,
                             binary_command):
    """
    Create a binary command based on the logical operator token that is passed
    to this function

    Input:
        - token: the logical operator token that has been captured
        - token_list: the current tokens that have been captured
        - binary_command: the current unfinished binary command

    Output:
        - binary_command: the final unfinished binary command after processing
    """
    # Create new command from the token list
    new_command = Command(token_list)
    # If the new command has no token, raise unexpected token error
    if new_command.is_empty():
        raise UnexpectedTokenError(token.original_string)
    # Initialize the dictionary that contains the type of binary command
    # based on the operator type
    type_of_binary_command = {
        "||": Or_Command,
        "&&": And_Command
    }
    # If there is already a binary command that is incomplete
    if binary_command:
        # Finish the old binary command with the new command that has
        # just been created
        binary_command.right_command = new_command
        # Create a new binary command with the previous binary command
        # as its left command
        binary_command = type_of_binary_command[token.content](
            binary_command, None
        )
    # Else create a new binary command with the new command as its left
    # command
    else:
        binary_command = type_of_binary_command[token.content](
            new_command, None
        )
    # Return the binary command
    return binary_command


def process_semicolon_operator(token,
                               token_list,
                               binary_command,
                               command_list):
    """
    Complete an unfinished binary command or add a new command into
    command list when a semicolon appear

    Input:
        - token: the semicolon token that has been captured
        - token_list: the current tokens that have been captured
        - binary_command: the current unfinished binary command

    Output:
        - None: since there will be no unfinished binary command after
        this function.
    """
    # Create new command from the token list
    new_command = Command(token_list)
    # If the new command has no token, raise unexpected token error
    if new_command.is_empty():
        raise UnexpectedTokenError(token.original_string)
    # If there is already a binary command that is incomplete
    if binary_command:
        # Finish it with the new command as its right command
        binary_command.right_command = new_command
        # Add it into the command list
        command_list.append(binary_command)
    # Else add the new command into command list
    else:
        command_list.append(new_command)
    # Since there will be no unfinished binary command no matter after
    # this function, return None
    return None


def split_by_logical_operators_and_semicolon(initial_token_list):
    """
    Take the token list and split all tokens into commands
    by logical operators and semicolon

    Input:
        - token_list: the token list that will be splitted

    Output:
        - command_list: the final command list after split
    """
    # Initialize the return command list
    command_list = []
    # Initialize the token list, which will be the tokens of
    # the next command
    token_list = []
    # Initialize a variable that will store the last unfinished binary command
    binary_command = None
    # Initialize the counter
    index = 0
    # A loop to ensure that user input is correct
    while True:
        # Loop through the token list
        while index < len(initial_token_list):
            # Get current token
            token = initial_token_list[index]
            # If current token is not a logical operator or a semicolon
            # Add it to the token list
            if (isinstance(token, Operator_Token) and
                    token.content in ["||", "&&", ";"]):
                binary_command = process_special_operator(
                    token,
                    token_list,
                    binary_command,
                    command_list
                )
                # Reset the token list
                token_list = []
            # Else, change the unfinised binary command based on the operator
            else:
                token_list.append(token)
            # Increase the counter by 1
            index += 1
        # At the end of the token list, if a binary command isn't finished but
        # the token list is empty, ask the user to input more
        if binary_command and not token_list:
            additional_input = get_token_list(input(">"))
            token_list += additional_input
        # Else, the user input is correct,
        # process as if the token list ends with a semicolon
        else:
            process_semicolon_operator(token_list[-1],
                                       token_list,
                                       binary_command,
                                       command_list)
            break
    return command_list


##############################
#             Pipe           #
##############################


def is_token_a_pipe(token):
    """
    Check if a token is a pipe

    Input:
        - token: a token that needs to be checked

    Output:
        - False if the input token isn't a token type object or doesn't
        meet the requirement
    """
    if not isinstance(token, Token):
        print("is_token_a_pipe requires a Token object as its parameter")
        return False
    return isinstance(token, Operator_Token) and token.content == "|"


def split_command_list_by_pipe(command_list):
    """
    Split the command list by pipe

    Input:
        - command_list: A list of Command or Binary_Command Type objects that
        needs to be splitted.

    Output:
        - command_list: The list after being splitted
    """
    # Check input type
    if not isinstance(command_list, list):
        print("split_command_list_by_pipe requires a list object as",
              "its parameter")
        return
    # Loop through each command and split them
    for command in command_list:
        command = split_command_by_pipe(command)


def split_command_by_pipe(command):
    """
    Split a command by pipe

    Input:
        - command: a Command or Binary_Command type object

    Output:
        - command: the command after being splitted
    """
    # Check input type
    if not isinstance(command, (Command, Binary_Command)):
        print("split_command_by_pipe",
              "requires a Command or Binary_Command object as its parameter")
        return
    # If the command isn't a Command type object
    if not isinstance(command, Command):
        # Perform split on its left and right commands
        command.left_command = split_command_by_pipe(
            command.left_command
        )
        command.right_command = split_command_by_pipe(
            command.right_command
        )
    # Else if the Command has any pipe token in its token list, perform
    # split for single command on it
    elif any([is_token_a_pipe(token)
              for token in command.token_list]):
        command = split_single_command_by_pipe(command)
    # Return the final command
    return command


def split_single_command_by_pipe(command):
    """
    Split a single command by pipe

    Input:
        - command: A Command or Binary_Command type object

    Output:
        - pipe_command: The pipe command after being splitted
    """
    # Check input type
    if not isinstance(command, Command):
        print("split_single_command_by_pipe",
              "requires a Command object as its parameter")
        return
    # Initialize an empty token list
    token_list = []
    # Initialize a variable that will store the final pipe command
    pipe_command = None
    # Loop through the token list of the command
    for token in command.token_list:
        # If the token is a pipe and pipe command isn't empty
        if is_token_a_pipe(token) and pipe_command:
            # Complete the pipe command with a command created by the
            # token list
            pipe_command.right_command = Command(token_list)
            # Create a new pipe command with the previous pipe command as its
            # left side command
            pipe_command = Pipe_Command(pipe_command, None)
            # Reset the token list
            token_list = []
        # Elif the token is a pipe and pipe command is empty
        elif is_token_a_pipe(token):
            # Create new pipe command with a command created by the current
            # token list as its left side command
            pipe_command = Pipe_Command(Command(token_list), None)
            # Reset the token list
            token_list = []
        # Else
        else:
            # Add the token to the token list`
            token_list.append(token)
    # Finish the incomplete pipe command with the new command created
    # by the remaining token list
    pipe_command.right_command = Command(token_list)
    # Return the final pipe command
    return pipe_command


##############################
#         Redirection        #
##############################


def is_token_a_redirection(token):
    """
    Check if a token is a redirection operator

    Input:
        - token: a token that needs to be checked

    Output:
        - False if the input token isn't a token type object or doesn't
        meet the requirement
    """
    if not isinstance(token, Token):
        return False
    return (isinstance(token, Operator_Token) and
            token.content in [">", "<", "<<", ">>"])


def process_redirection_operator(token_list, standard_stream, index):
    """
    Add the redirection token into the stdin or stdout

    Input:
        - token_list: the command's token list
        - standard_stream: the token list that will be turned into the
        standard stream during execution
        - index: the index of the redirection operator token

    Output:
        - standard_stream: the final list of tokens
    """
    # If the redirection operator is at the end of the token list,
    # raise error
    try:
        # Initialize the list for standard stream by popping
        # the redirection operator out of the token list
        # and add it to the new list
        standard_stream = [token_list.pop(index)]
        # Remove all the separator token after the redirection operator
        while isinstance(token_list[index], Separator_Token):
            token_list.pop(index)
        # If the type of next token isn't one of the below, raise error
        if (type(token_list[index]) not in
                [
                    Word_Token,
                    Param_Expand_Token,
                    Double_Quote_Token,
                    Single_Quote_Token
        ]):
            raise UnexpectedTokenError(token_list[index].original_string)
        # Append the next token into the stream token list
        standard_stream.append(token_list.pop(index))
        return standard_stream
    except IndexError:
        raise UnexpectedTokenError("<newline>")


def process_redirection_for_single_command(command):
    """
    Process all redirection tokens in a single command

    Input:
        - command: A Command type object

    Output:
        - command: The command after processing
    """
    # Validate input
    if not isinstance(command, Command):
        print("process_redirection_for_single_command",
              "requires a Command object as its parameter")
        return command
    # If there is no redirection operator in the command's token list
    if all(not is_token_a_redirection(token)
           for token in command.token_list):
        # Return the command without changing anything
        return command
    # Initialize the counter
    index = 0
    # Loop through the token list of the command
    while index < len(command.token_list):
        # Get the current token at index position in the token list
        current_token = command.token_list[index]
        # If the token isn't a redirection operator
        if not is_token_a_redirection(current_token):
            # Skip it and move to the next token
            index += 1
            continue
        # Process redirection operators
        if current_token.content in ["<", "<<"]:
            command.stdin = process_redirection_operator(
                command.token_list,
                command.stdin,
                index
            )
        else:
            command.stdout = process_redirection_operator(
                command.token_list,
                command.stdout,
                index
            )
        index += 1
    return command


def process_redirection_for_command(command):
    """
    Process all redirection tokens in a command

    Input:
        - command: A Command or Binary_Command type object

    Output:
        - command: The command after processing
    """
    # If the command is a Binary_Command object
    if isinstance(command, Binary_Command):
        # Process redirection for both left and right commands
        command.left_command = process_redirection_for_command(
            command.left_command
        )
        command.right_command = process_redirection_for_command(
            command.right_command
        )
    # Elif the command is a Command type object
    elif isinstance(command, Command):
        command = process_redirection_for_single_command(
            command
        )
    # Else, print out an error message because input type is incorrect
    else:
        print("process_redirection_for_command",
              "requires a Command or Binary_Command type object as",
              "its parameter")
    return command


def process_redirection_for_command_list(command_list):
    """
    Process all redirection tokens for each command in a command list

    Input:
        - command_list: a list of Command or Binary_Command type objects
    """
    # Validate input
    if not isinstance(command_list, list):
        print("process_redirection requires a list object as its parameter")
        return
    # Process the direction token for each command in command list
    for command in command_list:
        command = process_redirection_for_command(command)


##############################
#           Subshell         #
##############################


def check_subshell_syntax_for_single_command(command):
    """
    Check if the subshell token has correct syntax in a single command

    Input:
        - command: a Command type object

    Output:
        - token: A token that causes syntax error for the subshell.
        None if there is no syntax error for the subshell
    """
    if not isinstance(command, Command):
        print("check_subshell_syntax_for_single_command",
              "requires a Command object as its parameter")
        return None
    for token in command.token_list:
        if not isinstance(token, (Subshell_Token, Operator_Token)):
            return token
    return None


def check_subshell_syntax_for_command(command):
    """
    Check if the subshell token is in the correct syntax in a command

    Input:
        - command: A Command or Binary_Command type object
    """
    # Validate input
    if not isinstance(command, (Command, Binary_Command)):
        print("check_subshell_syntax_for_command",
              "requires a Command or Binary_Command object as its parameter")
        return
    # If the command is a Binary_Command, check syntax for its left and right
    # commands
    if isinstance(command, Binary_Command):
        print(command)
        check_subshell_syntax_for_command(command.left_command)
        check_subshell_syntax_for_command(command.right_command)
    # Else check syntax for the single command only if there is a subshell
    # token in its token list
    else:
        if any(isinstance(token, Subshell_Token)
               for token in command.token_list):
            token = check_subshell_syntax_for_single_command(command)
            if token:
                raise UnexpectedTokenError(token.original_string)


def check_subshell_syntax(command_list):
    """
    Check if the subshell token is in the correct syntax in command list

    Input:
        - command_list: a list of Command or Binary_Command type objects
    """
    # Validate input
    if not isinstance(command_list, list):
        print("check_subshell_syntax requires a list object as its parameter")
        return
    # Check syntax for each command in command list
    for command in command_list:
        check_subshell_syntax_for_command(command)
    return command_list


##############################
#          MAIN FLOW         #
##############################


def get_command_list(token_list):
    """
    From the token string, filter and split the tokens into commands

    Input:
        - token_list: a list of Token-type objects

    Output:
        - command_list: a list of Command type or Binary_Command type objects
        that are derived from the token_list
    """
    # Check if the input is correct
    if not isinstance(token_list, list):
        print("get_command_list requires a list object as its parameter")
        return []
    # Start by splitting command by logical operators and semicolon
    command_list = split_by_logical_operators_and_semicolon(token_list)
    # Split the command list using the pipe operator as delimiter
    split_command_list_by_pipe(command_list)
    # Process redirection operators in command list
    process_redirection_for_command_list(command_list)
    # Check syntax for subshell in the command list
    check_subshell_syntax(command_list)
    return command_list
