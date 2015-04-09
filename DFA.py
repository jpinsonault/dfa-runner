from collections import namedtuple
from collections import defaultdict

DFA = namedtuple("DFA", ["states", "alphabet", "transitions", "start_state", "final_states"])
# tuple of state -> character
T = namedtuple("transition_key", ["state", "character"])


class InvalidDFA(Exception):
    pass


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
        raise InvalidDFA("A transition goes to an invalid state")

    ### Make sure each state has a transition for each character in the alphabet
    # Holds all the characters found in the transition for each state
    state_character_sets = defaultdict(set)

    for state, character in transitions.keys():
        state_character_sets[state].add(character)

    for state, character_set in state_character_sets.items():
        if character_set != alphabet:
            error = "State '{}' doesn't contain a transition for each character in the alphabet".format(state)
            raise InvalidDFA(error)
