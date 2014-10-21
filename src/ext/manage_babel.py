# coding=utf-8
# Copyright 2013 Janusz Skonieczny

from flask_script import Command

# TODO: 29.11.13 wooyek

class BabelCommand(Command):
    def run(self):
        from babel.messages.frontend import CommandLineInterface as BabelCLI
        BabelCLI.run()

