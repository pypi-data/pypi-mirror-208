#!/usr/bin/env python
# -*- coding: UTF-8 -*-

####################################################################################
# Command line tool to launch firebird console
# Usage:
#     fbconsole args
# The args format is the same as you pass to manage.py in a regular django app
####################################################################################

import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firebirdconsole.firebirdconsole.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
