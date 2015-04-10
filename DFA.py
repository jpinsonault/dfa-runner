"""
    CS311
    Author: Joe Pinsonault

    Contains objects and functions for parsing, creating, running,
    and validating DFAs.

    DFAs are stored in `DFA` tuples, which contain the set of states,
    transition function, and so on.

    DFAs can be run through the `validate_dfa` function to ensure they've
    been defined correctly.

    The `dfa_accepts` function will determine if a DFA accepts an input string

    `parse_dfa_from_yaml` takes in a yaml document and parses out the needed
    information and creates a `DFA` object
"""

from collections import namedtuple
from collections import defaultdict

import yaml

DFA = namedtuple("DFA", ["states",
                         "alphabet",
                         "transitions",
                         "start_state",
                         "final_states"])


# Catch-all exception for something being wrong with the DFA
class InvalidDFA(Exception):
    pass


##############
# Running DFAs
##############

def dfa_accepts(dfa, input_string):
    """Returns true if dfa accepts input_string"""
    current_state = dfa.start_state

    try:
        # If the input is an empty string, the loop will just fall through,
        # doing nothing, leaving the current state as the start state
        for character in input_string:
            current_state = dfa.transitions[(current_state, character)]

    # A KeyError will be raised if the combination of the input character
    # and the current state isn't in the transition function
    except KeyError as e:
        state, character = e.args[0]

        # If the input character isn't in the alphabet, this is ok. Just reject the string
        if character not in dfa.alphabet:
            return False
        # Else something unexpected has gone wrong
        # Note: this shouldn't be reachable if the DFA has been put through the validator
        else:
            error = "Something went wrong when attempting transition from state '{}' on input '{}'"
            raise InvalidDFA(error.format(state, character))

    # Return true if the last state is in the set of final states
    return current_state in dfa.final_states


#############
# Validation
#############
def validate_dfa(dfa):
    """
        Wrapper around the various validation functions

        A DFA is valid if:
        - The final states are all in dfa.states
        - The start state is in the dfa.states
        - Each entry in the transition function goes from a state in dfa.states
           to a state in dfa.states
        - The transition function only transitions on characters that are in dfa.alphabet
        - The transition function has a transition for each character in dfa.alphabet
           for each state in dfa.states
    """
    validate_final_states(dfa.states, dfa.final_states)

    validate_start_state(dfa.states, dfa.start_state)

    validate_transitions(dfa.states, dfa.transitions, dfa.alphabet)


def validate_final_states(states, final_states):
    final_states_valid = all(final_state in states for final_state in final_states)

    if not final_states_valid:
        raise InvalidDFA("Accepting states should be in the list of states")


def validate_start_state(states, start_state):
    if start_state not in states:
        raise InvalidDFA("Start state should be in the list of states")


def validate_transitions(states, transitions, alphabet):
    # All input characters to the transition function must be in the alphabet
    valid_alphabet = all(character in alphabet for state, character in transitions.keys())

    if not valid_alphabet:
        invalid_characters = set(c for s, c in transitions.keys() if c not in alphabet)
        error = "A transition uses characters that aren't in the DFA's alphabet: {}"
        raise InvalidDFA(error.format(invalid_characters))

    # All input states must be in the set of states
    valid_from_states = all(state in states for state, character in transitions.keys())

    if not valid_from_states:
        raise InvalidDFA("A transition goes from an invalid state")

    # All output states must be in the set of states
    valid_to_states = all(state in states for state in transitions.values())

    if not valid_to_states:
        raise InvalidDFA("A transition goes to an invalid state.\n{}".format(transitions))

    # Make sure each state has a transition for each character in the alphabet
    # Holds all the characters found in the transition for each state
    state_character_sets = defaultdict(set)

    # Collect characters
    for state, character in transitions.keys():
        state_character_sets[state].add(character)

    # Make sure each set of characters is the same as the alphabet
    for state, character_set in state_character_sets.items():
        if character_set != alphabet:
            error = "State '{}' doesn't contain a transition for each character in the alphabet".format(state)
            raise InvalidDFA(error)

#####################
# Loading and parsing
#####################

def load_yaml(filename):
    """Return the parsed yaml document"""
    with open(filename, "r") as yaml_file:
        return yaml.load(yaml_file)


def parse_dfa_from_yaml(yaml_doc):
    """
        Parses the DFA information out of a yaml document
        Returns a DFA object

        Runs the alphabet and input characters in the transition function
        through str() since they can be written as integers in the yaml file

        This seems better than forcing the user to put everything in quotes inside
        the yaml files
    """

    states = set(yaml_doc["states"])
    alphabet = set(str(x) for x in yaml_doc["alphabet"])
    transitions_yaml = yaml_doc["transitions"]
    start_state = yaml_doc["start_state"]
    final_states = set(yaml_doc["final_states"])

    transitions = {}

    # Transform the dictionary of dictionaries from the yaml file into
    # a dictionary of:
    #   (input_state, input_character): output_state
    # mappings
    #
    # Top level is the input state
    for input_state, character_to_state_dict in transitions_yaml.items():
        for input_character, output_state in character_to_state_dict.items():
            # Create new entry in transitions
            transitions[(input_state, str(input_character))] = output_state

    return DFA(states, alphabet, transitions, start_state, final_states)
