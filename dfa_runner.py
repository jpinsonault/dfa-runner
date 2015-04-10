#!/usr/bin/env python

"""
    CS311
    Author: Joe Pinsonault

    Loads a DFA from a Yaml file and determines if it accepts
    the input string. DFAs are validated before being run.

    usage: dfa_runner.py [-h] dfa_yaml input_string

    positional arguments:
      dfa_yaml      Yaml file defining a DFA
      input_string  String to run through the DFA

    example:
      ./dfa_runner.py test_dfas/contains_substring_00.yaml "10101010101"
"""

import sys
import argparse

from DFA import validate_dfa
from DFA import dfa_accepts
from DFA import load_yaml
from DFA import parse_dfa_from_yaml


def parse_args(argv):
    description = "Loads a DFA and determines if it accepts the input string"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('dfa_yaml', help='Yaml file defining a DFA')
    parser.add_argument('input_string', help='String to run through the DFA')
    args = parser.parse_args(argv[1:])

    return args


def main(args):
    description, dfa = load_dfa(args.dfa_yaml)

    print("Loaded DFA: {}".format(description))
    print("Input string: {}".format(args.input_string))

    validate_dfa(dfa)

    accepts = dfa_accepts(dfa, args.input_string)

    if accepts:
        print("DFA accepts string '{}'".format(args.input_string))
    else:
        print("DFA rejects string '{}'".format(args.input_string))


def load_dfa(yaml_filename):
    dfa_doc = load_yaml(yaml_filename)

    dfa = parse_dfa_from_yaml(dfa_doc)

    description = dfa_doc["description"]

    return description, dfa


if __name__ == '__main__':
    sys.exit(main(parse_args(sys.argv)))
