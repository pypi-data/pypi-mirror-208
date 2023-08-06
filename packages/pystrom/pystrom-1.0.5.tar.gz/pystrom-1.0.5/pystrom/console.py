# Rafael Urben, 2021
#
# https://github.com/rafaelurben/python-mystrom

import sys
import argparse

from pystrom.search import MyStromSearch
from pystrom.utils import log

class MyStromCommandParser(object):
    """MyStrom command line utility"""

    COMMANDS = ["search"]

    def __get_usage__(self):
        doc = "pystrom <command> [args]\n\nPossible commands:\n"
        for cmd in self.COMMANDS:
            doc += cmd.ljust(12)+getattr(self, cmd).__doc__+"\n"
        return doc+"\n"

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Control MyStrom devices',
            usage=self.__get_usage__())
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            log('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    # Commands

    def search(self):
        """Search MyStrom devices in your local network"""
        parser = argparse.ArgumentParser(description=self.search.__doc__)
        parser.add_argument('--live', action='store_true', 
            help="Keep connection open until manually stopped.")
        args = parser.parse_args(sys.argv[2:])
        if args.live:
            MyStromSearch.searchlive()
        else:
            MyStromSearch.searchall()
