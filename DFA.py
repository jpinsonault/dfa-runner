from collections import namedtuple
from collections import defaultdict

DFA = namedtuple("DFA", ["states",
                         "alphabet",
                         "transitions",
                         "start_state",
                         "final_states"])


class InvalidDFA(Exception):
    pass


#############
# Running DFAs
#############

# Returns true if dfa accepts input_string
def dfa_accepts(dfa, input_string):
    current_state = dfa.start_state
    try:
        for character in input_string:
            current_state = dfa.transitions[(current_state, character)]
    except KeyError as e:
        state, character = e.args[0]

        # If the input character isn't in the alphabet, reject the string
        if character not in dfa.alphabet:
            return False
        # Else something unexpected has gone wrong
        else:
            error = "Something went wrong when attempting transition from state '{}' on input '{}'"
            raise InvalidDFA(error.format(state, character))

    return current_state in dfa.final_states


#############
# Validation
#############
def validate_dfa(dfa):
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
    # check transition characters are in alphabet
    valid_alphabet = all(character in alphabet for state, character in transitions.keys())

    if not valid_alphabet:
        raise InvalidDFA("A transition uses a character that's not in the DFA's alphabet")

    valid_from_states = all(state in states for state, character in transitions.keys())

    # A transition is going from a state that doesn't exist
    if not valid_from_states:
        raise InvalidDFA("A transition goes from an invalid state")

    valid_to_states = all(state in states for state in transitions.values())

    # A transition goes to a state that doesn't exist
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
