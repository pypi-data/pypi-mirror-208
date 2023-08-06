# coding=utf-8
'''
Copyright (C) 2023 Siogeen

Created on 4.1.2023

@author: Reimund Renner
'''

import argparse

def getParser():
    parser = argparse.ArgumentParser(
        description='Check for IO-Link masters and devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  python -m siogeen.tools.cli.IoddComChecker
  python -m siogeen.tools.cli.IoddComChecker -a 10.0.0.17 -a 10.0.0.19 --auto''')
    parser.add_argument("-a", "--address",action='append',
                        help="specify one or more master addresses (default all)")
    parser.add_argument("--auto", action='store_true',
                        help="activate master ports if all are disabled")
    parser.add_argument("--version", action='store_true',
        help="print version")

    return parser

if __name__ == '__main__':
    parser = getParser()
    args = parser.parse_args()
    #args = parser.parse_args(['--auto'])
    #args = parser.parse_args(['-a', '/dev/ttyUSB0'])
    #args = parser.parse_args(['-a', '192.168.178.77'])
    #args = parser.parse_args(['-a', '192.168.178.77', '-a', '192.168.178.73'])
    #args = parser.parse_args(['-a', '192.168.178.77', '--auto'])

    from siogeen.tools import IoddComChecker

    if args.version:
        print(f"IoddComChecker {IoddComChecker.__version__}")
    else:
        IoddComChecker.check(args.address, args.auto)
