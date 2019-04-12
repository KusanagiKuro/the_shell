#!/usr/bin/env python3

class base1:
    def __init__(self, content):
        self.content = content

class base2(base1):
    def foo(self):
        print(self.content)


a = base2(0)
a.foo()