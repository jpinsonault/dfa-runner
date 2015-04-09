#!/usr/bin/env python

"""
"""

import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('dfa_yaml', help='Yaml file defining a DFA')
    args = parser.parse_args()

    return args


def main(args):
    pass


if __name__ == '__main__':
    sys.exit(main(parse_args()))
