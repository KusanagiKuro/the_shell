#!/usr/bin/env python3
from token_definition import Double_Quote_Token, Single_Quote_Token,\
                             Param_Expand_Token, Param_Value_Token,\
                             Variable_Token, Operator_Token, Word_Token,\
                             Subshell_Token, Separator_Token
from readline import get_current_history_length, get_history_item
from utility import get_history_log
from exception import EventNotFoundError
from shell import Shell


#################################
#            Utility            #
#################################


def insert_token_to_list(content,
                         token_list,
                         position=None,
                         token_type="Word",
                         original_string=""):
    """
    Convert the content into a token and insert it to the list at
    certain position

    Input:
        - content: the content that will be converted
        - token_list: the list of tokens that the new token will be added
        to

    Output:
        - The new token if it has been inserted into the list
        - None if nothing get inserted
    """
    # Check if the input types are correct
    if (isinstance(content, (str, list)) and
            isinstance(token_list, list) and
            (isinstance(position, int) or
             position is None) and
            isinstance(token_type, str)) and content:
        # Create new token based on the token type
        if token_type == "Word":
            new_token = Word_Token(content, content)
        elif token_type == "Operator":
            new_token = Operator_Token(content, content)
        elif token_type == "Single_Quote":
            new_token = Single_Quote_Token(content, original_string)
        elif token_type == "Double_Quote":
            new_token = Double_Quote_Token(content, original_string)
        elif token_type == "Param_Expand":
            new_token = Param_Expand_Token(content, original_string)
        elif token_type == "Subshell":
            new_token = Subshell_Token(content, content)
        elif token_type == "Variable":
            new_token = Variable_Token(content, original_string)
        elif token_type == "Param_Value":
            new_token = Param_Value_Token(content, original_string)
        elif token_type == "Separator":
            new_token = Separator_Token(content, content)
        # If the token type matches none of the above, there
        # will be no token added into the list
        else:
            return None
        # If there is no position being specified, add the new
        # token to the end of the list
        if position is None:
            token_list.append(new_token)
        # Else insert it to the list at the position
        else:
            token_list.insert(position, new_token)
        return new_token
    return None


def get_string_from_list(list_of_char, begin, end):
    try:
        return "".join(char for char in list_of_char[begin:end+1])
    except IndexError:
        return ""


#################################
#        History Expansion      #
#################################


def search_history_log_with_string(history_log, search_string):
    """
    Search through the history log and return the command that
    started with certain string

    Input:
        - history_log: the history log of the shell
        - search_string: the string that we are looking for at the start
        of the command

    Output:
        - command: the command matched the condition. None if nothing is found.
    """
    for command in history_log[::-1]:
        if command.startswith(search_string):
            return command
    return None


def get_search_string_for_history_event(list_of_char, index):
    """
    Get the search string that is defined after the exclamation mark

    Input:
        - list_of_char: list of characters from the user's input
        - index: the index at which the history event starts
    
    Output:
        - search_string: the search string that will be used to search for
        certain command
        - index: the index at which the search string ends
    """
    # Initialize a variable that holds the search string
    search_string = list_of_char[index]
    # Increase index by one
    index += 1
    # Loop till the end of the string
    while index < len(list_of_char):
        # Get current character
        current_char = list_of_char[index]
        # Break if current character is a space, tab or newline
        if current_char in [" ", "\n", "\t"]:
            break
        # Else add it to the search string and move to next character
        else:
            search_string += current_char
            index += 1
    # Return search string and the index at which the searc string ends
    return search_string, index


def expand_history_event_starts_with_an_alphabet(list_of_char,
                                                 index,
                                                 history_log):
    """
    Replace the history event with the latest command that
    starts with a string defined after the exclamation mark

    Input:
        - list_of_char: a list of characters from the user's input
        - index: the index at which the history event starts
        - history_log: the history log of the shell
    """
    # Save the index as the begin index
    begin_index = index
    # Get the search string and the index at which the search string ends
    search_string, index = get_search_string_for_history_event(
        list_of_char, index
    )
    # Strip off the exclamation mark from the search string
    search_string = search_string.lstrip("!")
    # Get the command that starts with the search string from the history log
    command = search_history_log_with_string(history_log, search_string)
    # If a command is found, start replace the history event with the command
    if command:
        replace_history_event_in_list_of_char(list_of_char,
                                              command,
                                              begin_index,
                                              index)
        return
    # Raise error otherwise
    raise EventNotFoundError("!" + search_string)


def get_search_number_for_history_event(list_of_char, index):
    """
    Get the search string that is defined after the exclamation mark

    Input:
        - list_of_char: list of characters from the user's input
        - index: the index at which the history event starts
    
    Output:
        - search_string: the search string that will be used to search for
        certain command
        - index: the index at which the search string ends
    """
    # Initialize a variable that holds the search string
    search_number = list_of_char[index]
    # Increase index by one
    index += 1
    # Add the negative sign if needed
    if list_of_char[index] == "-":
        search_number += list_of_char[index]
        index += 1
    # Loop till the end of the string
    while index < len(list_of_char):
        # Get current character
        current_char = list_of_char[index]
        # If current character isn't a number, break
        if not current_char.isnumeric():
            break
        # Else add it to the search string and move to next character
        else:
            search_number += current_char
            index += 1
    # Return search string and the index at which the searc string ends
    return search_number, index


def validate_search_number(search_number, history_log):
    try:
        search_number = int(search_number.strip("!"))
        if search_number < 0:
            search_number = abs(search_number)
        if search_number > len(history_log) or\
           search_number < len(history_log) - 1000:
            raise EventNotFoundError("!" + str(search_number))
    except ValueError:
        raise EventNotFoundError("!-" + search_number)
    return search_number


def expand_history_event_at_certain_line(list_of_char,
                                         index,
                                         history_log,
                                         reverse=False):
    """
    Replace the history event with the latest command that
    starts with a string defined after the exclamation mark

    Input:
        - list_of_char: a list of characters from the user's input
        - index: the index at which the history event starts
        - history_log: the history log of the shell
        - reverse: a boolean which determines whether the list will be
        searched from latest to earliest or vice versa
    """
    # Save the index as the begin index
    begin_index = index
    # Get search number
    search_number, index = get_search_number_for_history_event(
        list_of_char, index
    )
    # Validate the search number
    search_number = validate_search_number(search_number, history_log)
    # Replace the history event with the command
    replace_history_event_in_list_of_char(list_of_char,
                                          history_log[search_number - 1]
                                          if not reverse else
                                          history_log[-search_number],
                                          begin_index,
                                          index)


def replace_history_event_in_list_of_char(list_of_char,
                                          extra_string,
                                          begin,
                                          end):
    """
    Replace the history event in list of character with the extra string

    Input:
        - list_of_char: the list of characters from user's input
        - extra_string: the string that will replace the history event
        - begin: the beginning index of the history event
        - end: the ending index of the history event
    """
    # Readjust the ending index
    if end == len(list_of_char):
        end -= 1
    # Pop all characters between begin index and end index in the
    # list
    for index in range(begin, end + 1):
        list_of_char.pop(begin)
    # Insert the characters from extra string into the list
    extra_character_list = [char for char in extra_string]
    while extra_character_list:
        list_of_char.insert(begin, extra_character_list.pop())


def expand_history_event(list_of_char, index, token_string):
    """
    Replace a history event with the command in the history file of the
    shell

    Input:
        - list_of_char: a list of character fomr the user's input
        - index: the index at which the history expansion start
        - token_string: the current token string
        - shell: the current shell instance
    """
    try:
        # Keep the beginning index
        begin_index = index
        # Get history log of the shell
        history_log = get_history_log()
        # Check the next character and process accordingly
        next_char = list_of_char[index + 1]
        # Search for latest command that starts with certain string
        # if next character is an alphabet
        if next_char.isalpha():
            expand_history_event_starts_with_an_alphabet(
                list_of_char,
                index,
                history_log
            )
        # Search for command at certain line in the history log if next
        # character is a number or a minus sign
        elif next_char is "-":
            expand_history_event_at_certain_line(
                list_of_char,
                index,
                history_log,
                True
            )
        elif next_char.isnumeric():
            expand_history_event_at_certain_line(
                list_of_char,
                index,
                history_log
            )
        # Get last command if next character is "!"
        elif next_char is "!":
            replace_history_event_in_list_of_char(list_of_char,
                                              history_log[-1] if history_log
                                              else "exit",
                                              index,
                                              index + 1)
        else:
            token_string += "!"
            return index + 1, token_string
        return begin_index, token_string
    except IndexError:
        token_string += "!"
        return index + 1, token_string


#################################
#       Escaped Character       #
#################################


def get_escaped_character(list_of_char, index, token_string):
    try:
        next_char = list_of_char[index + 1]
    except IndexError:
        list_of_char.extend([char for char in input(">")])
        try:
            next_char = list_of_char[index + 1]
        except IndexError:
            next_char = ""
    token_string += "\\" + next_char
    index += 1
    return list_of_char, index, token_string


#################################
#            Quoting            #
#################################


def get_double_quote_token(list_of_char, index, token_list):
    """
    Get the token created by the quoted string marked by the double quote

    Input:
        - list_of_char: The list of characters from user's input
        - index: The index that marked the start of the quoted string
        - token_list: The list that the token will be added into
        - shell: the current shell instance

    Output:
        - index: The end index of the quoted string
    """
    begin_index = index
    # Initialize the token string
    token_string = ""
    # Initialize the token list for the double quote token
    content_list = []
    # Loop until an unquoted/unescaped double quote is found
    while True:
        # Loop until end of string is reached
        while index < len(list_of_char):
            # Increase index by one
            index += 1
            # Break if index is equal to the string's length
            if index == len(list_of_char):
                break
            # Get current character at index position
            current_char = list_of_char[index]
            # If current character is a backslash, get escaped chracter
            if current_char is "\\":
                list_of_char, index, token_string = get_escaped_character(
                    list_of_char,
                    index,
                    token_string
                )
            # Else if the current character is an exclamation mark, start
            # history expansion
            elif current_char is "!":
                index, token_string = expand_history_event(
                    list_of_char, index, token_string
                )
                continue
            # If current character is an unquoted/unescaped double quote,
            # add a double quote token to the token list, return the current
            # index
            elif current_char is "\"":
                insert_token_to_list(token_string, content_list)
                insert_token_to_list(
                    content_list if content_list else [None],
                    token_list,
                    token_type="Double_Quote",
                    original_string=get_string_from_list(
                        list_of_char,
                        begin_index,
                        index
                    )
                )
                return index
            # If current character is an unquoted/unescaped dollar sign,
            # get dollar sign expand (variable or parameter expansion)
            elif current_char is "$":
                index, token_string = process_dollar_sign(
                    list_of_char,
                    index,
                    token_string,
                    content_list
                )
            # If current character is a <space>, insert the token string to
            # content list and reset it.
            elif current_char is " ":
                insert_token_to_list(
                    token_string,
                    content_list
                )
                insert_token_to_list(
                    " ",
                    content_list,
                    token_type="Separator"
                )
                token_string = ""
            # Else, just add current character to token string
            else:
                token_string += current_char
        # Ask user for more input if the quoted string is not closed
        list_of_char.extend([char for char in "\n" + input(">")])
    return index


def get_single_quote_token(list_of_char, index, token_list):
    """
    Get the token created by the quoted string marked by the single quote

    Input:
        - list_of_char: The list of characters from user's input
        - index: The index that marked the start of the quoted string
        - token_list: The list that the token will be added into

    Output:
        - index: The end index of the quoted string
    """
    begin_index = index
    # Initialize the token string
    token_string = ""
    # Loop until another single quote is found
    while True:
        # Loop until end of string is reached
        while index < len(list_of_char):
            # Increase index by 1
            index += 1
            # Break if index is equal to the length of input string
            if index == len(list_of_char):
                break
            # Get current character
            current_char = list_of_char[index]
            # If current character is a single quote,
            # insert a single quote token to token list
            # with token string as its content
            if current_char is "'":
                insert_token_to_list(
                    token_string,
                    token_list,
                    token_type="Single_Quote",
                    original_string=get_string_from_list(
                        list_of_char,
                        begin_index,
                        index
                    )
                )
                return index
            # Else, add current character to token string
            else:
                token_string += current_char
        # Ask user for more input if the quoted string is not closed
        list_of_char.extend([char for char in "\n" + input(">")])
    return index


#################################
#     Dollar Sign Processing    #
#################################


def get_param_expansion(list_of_char, index, token_list):
    """
    Get the parameter expansion token

    Input:
        - list_of_char: a list of characters from the user's input
        - index: the index at which the dollar sign that marks the
        parameter expansion
        - token_list: the list contains the tokens that will be returned
        after the lexing
    
    Output:
        - index: the ending index of the parameter expansion
    """
    # Keep the starting index
    begin_index = index
    # Initalize the list that will contains the variable name, operator and
    # substitute value
    content_list = []
    # Initialize the variables that will keep the current value of the variable
    # name, operator and substitute value
    param_name = ""
    param_operator = ""
    param_value = []
    # Increase the index to the start of the parameter expansion starts
    index += 2
    # Loop till the user input is correct
    while True:
        # If the operator and substitute value are empty, get the variable name
        if not param_operator and not param_value:
            index, param_name = get_param_name(
                list_of_char,
                index,
                content_list,
                param_name
            )
        # If the substitute value is empty, get the operator
        if not param_value:
            index, param_operator = get_param_operator(
                list_of_char,
                index,
                content_list,
                param_operator
            )
        # Always check and get the parameter value
        index, param_value = get_param_value(
            list_of_char,
            index,
            content_list,
            param_value
        )
        # Check if the parameter expansion has been closed, if not, ask the user
        # for more input
        try:
            current_char = list_of_char[index]
            # If the parameter expansion has been closed, add it to the
            # token list and return the ending index
            if current_char is "}":
                insert_token_to_list(
                    content_list if content_list else [None],
                    token_list,
                    token_type="Param_Expand",
                    original_string=get_string_from_list(
                        list_of_char,
                        begin_index,
                        index
                    )
                )
                return index
        except IndexError:
            pass
        list_of_char.extend([char for char in (" " + input(">"))])
    return index


def get_param_name(list_of_char, index, token_list, current_value):
    """
    Get the parameter name in the parameter expansion

    Input:
        - list_of_char: The list of characters from user's input
        - index: The index that marked the start of the parameter name
        - token_list: The list that the token will be added into
        - current_value: the current value of the parameter name

    Output:
        - index: The end index of the parameter name
    """
    # Keep current index
    begin_index = index
    # Set token string to the current value
    token_string = current_value
    # If the token string is empty and the current character isn't
    # an alphabet or underscore, return
    if not token_string and not (list_of_char[index].isalpha() or
                                 list_of_char[index] == "_"):
        return index, token_string
    # Loop till the end of list
    while index < len(list_of_char):
        # Get current character
        current_char = list_of_char[index]
        # If current character is a number or a character or an underscore,
        # add it to the variable name
        if current_char.isalnum() or current_char is "_":
            token_string += current_char
        # Else add the variable name to the token list
        # return the index if current character is the closing brace, otherwise index + 1
        else:
            insert_token_to_list(
                token_string,
                token_list,
                token_type="Variable",
                original_string=get_string_from_list(
                    list_of_char,
                    begin_index,
                    index
                )
            )
            return index + 1 if current_char != "}" else index, token_string
        index += 1
    return index, token_string


def get_param_operator(list_of_char, index, token_list, current_value):
    """
    Get the parameter operator in the parameter expansion

    Input:
        - list_of_char: The list of characters from user's input
        - index: The index that marked the start of the parameter operator
        - token_list: The list that the token will be added into
        - current_value: the current value of the parameter operator

    Output:
        - index: The end index of the parameter operator
    """
    # Create a list of valid operators
    operators = ["##", "%%", "%", "#", ":", ":?", ":-",
                 ":=", ":+"]
    # Set token string to the current value
    token_string = current_value
    # Loop till the end of list
    while index < len(list_of_char):
        # Get current character
        current_char = list_of_char[index]
        # If the current character cannot form an operator with previous
        # characters in token string, add the token to the token list as
        # an operator token. Return the index, token string
        if token_string + current_char not in operators:
            insert_token_to_list(
                token_string,
                token_list,
                token_type="Operator"
            )
            return index, token_string
        # Else add it to the token string
        else:
            token_string += current_char
        index += 1
    return index, token_string


def get_param_value(list_of_char,
                    index,
                    token_list,
                    current_content_list):
    """
    Get the parameter operator in the parameter expansion

    Input:
        - list_of_char: The list of characters from user's input
        - index: The index that marked the start of the substitute value
        - token_list: The list that the token will be added into
        - current_content_list: the current value of the substitute value

    Output:
        - index: The end index of the substitute value
    """
    # Initialize the token string
    token_string = ""
    # Initialize the content list
    content_list = current_content_list
    # Loop till the end of list
    while index < len(list_of_char):
        current_char = list_of_char[index]
        # Pass through all the new space if the content list is empty
        if current_char is " " and not content_list:
            pass
        # Process backslash
        elif current_char is "\\":
            list_of_char, index, token_string = get_escaped_character(
                list_of_char,
                index,
                token_string
            )
        # Else if the current character is an exclamation mark
        elif current_char is "!":
            index, token_string = expand_history_event(
                list_of_char, index, token_string
            )
            continue
        # Else if the current character is the closing brace,
        # add the content list to the token list as a param_value token
        # Return the index and current content list
        elif current_char is "}":
            insert_token_to_list(
                token_string,
                content_list,
                token_type="Word"
            )
            insert_token_to_list(
                content_list if content_list else [None],
                token_list,
                token_type="Param_Value"
            )
            return index, content_list
        # Else if the current character is ":",
        # add the previous token string to the content list as word token
        # and add the extra operator token into the param_value
        elif current_char is ":":
            insert_token_to_list(
                token_string,
                content_list,
                token_type="Word"
            )
            insert_token_to_list(
                ":",
                content_list,
                token_type="Operator"
            )
            token_string = ""
        # Add previous token string to token list if current character is
        # a space or new line
        elif current_char in [" ", "\n", "\t"]:
            insert_token_to_list(
                token_string,
                content_list,
                token_type="Word"
            )
            insert_token_to_list(
                current_char,
                content_list,
                token_type="Separator"
            )
            token_string = ""
        # Else if the current character is a quote, process according to its type
        elif current_char in ["'", "\""]:
            insert_token_to_list(
                token_string,
                content_list,
                token_type="Word"
            )
            index = (
                get_single_quote_token(
                    list_of_char,
                    index,
                    content_list
                )
                if current_char is "'" else
                get_double_quote_token(
                    list_of_char,
                    index,
                    content_list
                )
            )
        # Else if current character is a dollar sign, process dollar sign expansion
        elif current_char is "$":
            index, token_string = process_dollar_sign(
                list_of_char,
                index,
                token_string,
                content_list
            )
        # Else just add it to the token string
        else:
            token_string += current_char
        index += 1
    # If end of list is reached, add the remaining token string to the token list
    insert_token_to_list(
        token_string,
        content_list,
        token_type="Word"
    )
    return index, content_list


def get_variable(list_of_char, index, token_list):
    """
    Get the variable token

    Input:
        - list_of_char: a list of characters from the user's input
        - index: the index at which the dollar sign that marks the
        variable token is
        - token_list: the list contains the tokens that will be returned
        after the lexing
    
    Output:
        - index: the ending index of the parameter expansion
    """
    # Initialize the string that will keep the variable name
    token_string = ""
    # Loop till the end of list
    while index < len(list_of_char):
        try:
            next_char = list_of_char[index + 1]
            if next_char.isalnum() or next_char is "_":
                token_string += next_char
            else:
                insert_token_to_list(
                    token_string,
                    token_list,
                    token_type="Variable"
                )
                return index
        # Add the token string into the token list when end of string is reached
        except IndexError:
            if token_string:
                insert_token_to_list(
                    token_string,
                    token_list,
                    token_type="Variable"
                )
            break
        index += 1
    return index


def get_dollar_sign_expand(list_of_char, index, token_list):
    """
    Get the token marked by the dollar sign

    Input:
        - list_of_char: a list of characters from the user's input
        - index: the index in the above list at which the dollar sign is
        - token_list: the list of token that will be returned at the end
        of the lexing process

    Output:
        - index: the index at which the expansion ends
    """
    try:
        next_character = list_of_char[index + 1]
        # If the next character is a curly bracket, this means it's
        # a parameter expansion. Return the end index of that parameter
        # expansion
        if next_character is "{":
            return get_param_expansion(
                list_of_char,
                index,
                token_list
            )
        # If next character is a letter or an underscored, it's a
        # variable. Return the end index of that variable token
        elif next_character.isalpha() or next_character is "_":
            return get_variable(
                list_of_char,
                index,
                token_list
            )
        # Else the dollar sign doesn't have special meaning
        else:
            return index
    except IndexError:
        return index


def process_dollar_sign(list_of_char,
                        index,
                        token_string,
                        token_list):
    """
    See if the dollar sign's a normal character, a
    variable or an expansion and process accordingly.

    Input:
        - list_of_char: a list of characters from the user's input
        - index: the index in the above list at which the dollar sign is
        - token_string: the current token string
        - token_list: the list of token that will be returned at the end
        of the lexing process
    
    Output:
        - index: the index at which the expansion ends
        - token_string: the token string after modification
    """
    end_index = get_dollar_sign_expand(
        list_of_char,
        index,
        token_list
    )
    # If the end index of dollar sign expand is the same as the
    # current index (meaning the dollar sign stand alone), append
    # it to the token string
    if end_index == index:
        current_char = list_of_char[index]
        token_string += current_char
    # Else, insert the previous token string to the content list,
    # reset the token string and set index equal to the end index
    else:
        insert_token_to_list(
            token_string,
            token_list,
            -1
        )
        token_string = ""
        index = end_index
    return index, token_string


#################################
#            Subshell           #
#################################


def get_subshell_token(list_of_char, index, token_list):
    begin_index = index
    current_char = None
    previous_char = None
    index += 1
    while True:
        while index < len(list_of_char):
            current_char = list_of_char[index]
            if previous_char is "\\":
                pass
            elif current_char in ["'", "$", '"', "("]:
                special_character_function = {
                    "'": get_single_quote_token,
                    "$": get_dollar_sign_expand,
                    '"': get_double_quote_token,
                    "(": get_subshell_token
                }
                index = special_character_function[current_char](
                    list_of_char,
                    index,
                    []
                )
            elif current_char is ")":
                insert_token_to_list(
                    get_string_from_list(
                        list_of_char,
                        begin_index,
                        index
                    ),
                    token_list,
                    token_type="Subshell"
                )
                return index
            index += 1
        list_of_char.extend([char for char in ";" + input(">")])
    return index


#################################
#           Main Lexer          #
#################################


def get_token_list(input_string):
    """
    Convert the user input into a token list

    Input:
        - input_string: The string that the user has input
        - shell: the current shell instance

    Output:
        - token_list: the list of tokens after conversion
        - None if the input is incorrect
    """
    # If the input is incorrect, return None
    if not isinstance(input_string, str):
        print("input_string parameter must be a str type object")
        return None
    operators = ['||', '|', '>', '<', '<<', '>>', '&&', ';']
    quotes_and_braces = ["'", '"', "("]
    separators = [" ", "\n"]
    # Convert the string into list so it becomes mutable
    list_of_char = [char for char in input_string]
    # Initialize the token list and token string (which will be used
    # to convert into token)
    token_list = []
    token_string = ''
    # Initialize a variable to track the index
    index = 0
    # Initialize a variable to track the previous character
    previous_char = ""
    # Loop through the input string one by one.
    while index < len(list_of_char):
        # Get current character at current index
        current_char = list_of_char[index]
        # If previous character and current character can be combined
        # to create an operator
        if previous_char + current_char in operators:
            # Add current character to token string
            token_string = previous_char + current_char
        # Else if current character can be an operator
        elif current_char in operators:
            # Convert and add current token string to token list
            insert_token_to_list(token_string, token_list)
            # New token string starts with current character
            token_string = current_char
        # Else if the token string is an operator
        elif token_string in operators:
            # Convert and add current token string as an operator token
            # to token list
            insert_token_to_list(token_string, token_list,
                                 token_type="Operator")
            token_string = ""
            continue
        # Else if the current character is an exclamation mark
        elif current_char is "!":
            index, token_string = expand_history_event(list_of_char, index, token_string)
            continue
        # Else if current character is a <backslash>
        elif current_char is "\\":
            list_of_char, index, token_string = get_escaped_character(
                list_of_char,
                index,
                token_string
            )
        # Else if current character is a $
        elif current_char is "$":
            index, token_string = process_dollar_sign(
                list_of_char,
                index,
                token_string,
                token_list
            )
        # Else if current character is a <double_quote>
        # or a <space>
        # or a <single_quote>
        # or left parentheses
        elif current_char in quotes_and_braces + separators:
            # Convert and add current token string to token list
            insert_token_to_list(
                token_string,
                token_list
            )
            # New token string will be empty
            token_string = ""
            # If current character is not a <space>
            if current_char in ["\"", "'", "("]:
                # Initialize the dictionary that contains the name of
                # the functions that will get the token
                get_token_functions = {
                    "\"": get_double_quote_token,
                    "'": get_single_quote_token,
                    "(": get_subshell_token
                }
                # Run the get token function base on the current character
                # and return the index
                index = get_token_functions[current_char](
                    list_of_char,
                    index,
                    token_list
                )
            else:
                insert_token_to_list(
                    current_char,
                    token_list,
                    token_type="Separator"
                )
        # Else add current character to token string
        else:
            token_string += current_char
        # Increase index by 1
        index += 1
        # Set previous character to current character
        previous_char = current_char
    # Add the current token string into the token list
    if token_string in operators:
        insert_token_to_list(
            token_string,
            token_list,
            token_type="Operator"
        )
    else:
        insert_token_to_list(
            token_string,
            token_list
        )
    return token_list, list_of_char
