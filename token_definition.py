#!/usr/bin/env python3
class Token:
    def __init__(self, content, original_string):
        self.content = content
        self.original_string = original_string

    def __str__(self):
        pass


class Word_Token(Token):
    def __str__(self):
        return "Word(%s)" % str(self.content)


class Double_Quote_Token(Token):
    def __str__(self):
        return "Double_Quote(%s)" % ", ".join([str(item)
                                              for item in self.content])


class Single_Quote_Token(Token):
    def __str__(self):
        return "Single_Quote(%s)" % str(self.content)


class Param_Expand_Token(Token):
    def __str__(self):
        return "Param_Expand(%s)" % ", ".join([str(item)
                                              for item in self.content])


class Operator_Token(Token):
    def __str__(self):
        return "Operator(%s)" % str(self.content)


class Variable_Token(Token):
    def __str__(self):
        return "Variable(%s)" % str(self.content)


class Param_Value_Token(Token):
    def __str__(self):
        return "Param_Value(%s)" % ", ".join([str(item)
                                             for item in self.content])


class Subshell_Token(Token):
    def __str__(self):
        return "Subshell(%s)" % self.content


class Separator_Token(Token):
    def __str__(self):
        return ("Seperator( )" if self.content == " "
                else "Separator(\\n)")


class Command:
    def __init__(self, token_list, stdin=None, stdout=None):
        self.token_list = token_list
        self.stdin = stdin
        self.stdout = stdout
        self.argument_string = []

    def is_empty(self):
        return False if len(self.token_list) else True

    def __str__(self):
        return "Command(TOKEN = (%s), STDIN = (%s), STDOUT = (%s))" % (
            ", ".join([str(item) for item in self.token_list]),
            ", ".join([str(item) for item in self.stdin])
            if self.stdin else "None",
            ", ".join([str(item) for item in self.stdout])
            if self.stdout else "None"
        )


class Binary_Command:
    def __init__(self, left_command, right_command=None,
                 stdin=None, stdout=None):
        self.left_command = left_command
        self.right_command = right_command
        self.stdin = None
        self.stdout = None

    def __str__(self):
        pass


class Or_Command(Binary_Command):
    def __str__(self):
        return "Or(%s, %s)" % (
            str(self.left_command),
            str(self.right_command)
        )


class And_Command(Binary_Command):
    def __str__(self):
        return "And(%s, %s)" % (
            str(self.left_command),
            str(self.right_command)
        )


class Pipe_Command(Binary_Command):
    def __str__(self):
        return "Pipe(%s, %s)" % (
            str(self.left_command),
            str(self.right_command)
        )
