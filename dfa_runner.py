#!/usr/bin/env python

"""
"""

import sys
import argparse
import yaml

from DFA import validate_dfa
from DFA import dfa_accepts
from DFA import DFA


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('dfa_yaml', help='Yaml file defining a DFA')
    parser.add_argument('input_string', help='String to run through the DFA')
    args = parser.parse_args()

    return args


def main(args):
    description, dfa = parse_dfa_from_yaml(args.dfa_yaml)

    print("Loaded DFA: {}".format(description))
    print("Input string: {}".format(args.input_string))

    validate_dfa(dfa)

    accepts = dfa_accepts(dfa, args.input_string)

    if accepts:
        print("DFA accepts string '{}'".format(args.input_string))
    else:
        print("DFA doens't accept string '{}'".format(args.input_string))



def parse_dfa_from_yaml(yaml_filename):
    with open(yaml_filename, "r") as yaml_file:
        dfa_doc = yaml.load(yaml_file)

    description = dfa_doc["description"]
    states = set(dfa_doc["states"])
    alphabet = set(dfa_doc["alphabet"])
    transitions_yaml = dfa_doc["transitions"]
    start_state = dfa_doc["start_state"]
    final_states = set(dfa_doc["final_states"])

    transitions = {}

    # Transform the dictionary of dictionaries from the yaml file into
    # a dictionary of
    # (input_state, input_character): output_state
    # mappings
    #
    # Top level is the input state
    for input_state, character_to_state_dict in transitions_yaml.items():
        # Loop through dictionary of input_character->output_state mappings
        for input_character, output_state in character_to_state_dict.items():
            # Create new entry in transitions
            transitions[(input_state, input_character)] = output_state

    return description, DFA(states, alphabet, transitions, start_state, final_states)

if __name__ == '__main__':
    sys.exit(main(parse_args()))
