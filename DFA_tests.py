"""
    CS311
    Author: Joe Pinsonault

    Contains unit tests for the DFA module

    Tests all the DFAs in ./test_dfas
    Each DFA yaml file includes a list of strings it should accept and
    a list it shouldn't. These are all tested here

    In addition, each DFA contains a regular expression describing the
    dfa's language.
    This is used by the exrex module to generate thousands of strings from the
    language that the DFA should accept.

    exrex generates strings from short to long. For example, if the language is
        (.{0})|(xy[xy]*)
    ie, the empty string or strings starting with 'xy', the first string it generates
    is the empty string, followed by 'xy', and then it begins to add 'x's and 'y's
    to the end of the string

    See https://github.com/asciimoo/exrex for more details
"""

import unittest
from glob import glob
from collections import namedtuple
from itertools import islice

import exrex

from DFA import DFA
from DFA import validate_dfa
from DFA import dfa_accepts
from DFA import load_yaml
from DFA import parse_dfa_from_yaml
from DFA import validate_final_states
from DFA import validate_start_state
from DFA import validate_transitions
from DFA import InvalidDFA

# Convenience class so that I can reference the parameters to the
# transition function by name
# tuple of (input state -> input character)
T = namedtuple("transition_key", ["state", "character"])

# Container for testing DFAs
DFATest = namedtuple("DFATest", ["yaml", "dfa"])


def take_from(iterator, i):
    """
        Wrapper around islice
        yields i items from iterator
    """
    yield from islice(iterator, i)


class UnexpectedRejection(Exception):
    """Exception for DFAs that unexpectedly reject a string"""
    def __init__(self, dfa_description, input_string, regex):
        msg = "DFA '{}' rejected '{}' from regex '{}'".format(dfa_description, input_string, regex)
        super(UnexpectedRejection, self).__init__(msg)


class UnexpectedAccept(Exception):
    """Exception for DFAs that unexpectedly accept a string"""
    def __init__(self, dfa_description, input_string, regex):
        msg = "DFA '{}' accepted '{}' from regex '{}'".format(dfa_description, input_string, regex)
        super(UnexpectedAccept, self).__init__(msg)


class TestDfaStartStateAndFinalStates(unittest.TestCase):
    """
        Tests that make sure the validation functions catch valid
        and invalid start states and final states
    """
    def setUp(self):
        self.states = {1, 2, 3, 4}

    def test_valid_final_states(self):
        final_states = {2, 4}

        # Test that it doesn't throw
        validate_final_states(self.states, final_states)

    def test_invalid_final_state(self):
        with self.assertRaises(InvalidDFA) as e:
            final_states = {5}

            validate_final_states(self.states, final_states)

        error = "Accepting states should be in the list of states"
        self.assertTrue(error in str(e.exception))

    def test_invalid_final_state_with_valid_state(self):
        with self.assertRaises(InvalidDFA) as e:
            # 1 is in states, 6 is not
            final_states = {1, 6}

            validate_final_states(self.states, final_states)

        error = "Accepting states should be in the list of states"
        self.assertTrue(error in str(e.exception))

    def test_valid_start_state(self):
        start_state = 1

        validate_start_state(self.states, start_state)

    def test_invalid_start_state(self):
        # 1 is in states, 6 is not
        start_state = 6

        with self.assertRaises(InvalidDFA) as e:
            validate_start_state(self.states, start_state)

        error = "Start state should be in the list of states"
        self.assertTrue(error in str(e.exception))


class TestTransitions(unittest.TestCase):
    """
        Tests for validating transition functions
    """
    def setUp(self):
        self.states = {1, 2, 3, 4}

        self.alphabet = {"a", "b"}

    def test_valid_transitions(self):
        transitions = {
            T(1, "a"): 2,
            T(1, "b"): 2,
            T(2, "a"): 3,
            T(2, "b"): 3,
            T(3, "a"): 4,
            T(3, "b"): 4,
            T(4, "a"): 1,
            T(4, "b"): 1,
        }
        validate_transitions(self.states, transitions, self.alphabet)

    def test_invalid_character_in_transitions(self):
        transitions = {
            T(1, "a"): 2,
            T(1, "b"): 2,
            T(2, "a"): 3,
            T(2, "b"): 3,
            T(3, "a"): 4,
            T(3, "b"): 4,
            T(4, "a"): 1,
            T(4, "c"): 1,
        }

        with self.assertRaises(InvalidDFA) as e:
            validate_transitions(self.states, transitions, self.alphabet)

        error = "A transition uses characters that aren't in the DFA's alphabet: {'c'}"

        self.assertTrue(error in str(e.exception), str(e.exception))

    def test_invalid_from_state_in_transitions(self):
        transitions = {
            T(300, "a"): 2,
            T(1, "b"): 2,
            T(2, "a"): 3,
            T(2, "b"): 3,
            T(3, "a"): 4,
            T(3, "b"): 4,
            T(4, "a"): 1,
            T(4, "b"): 1,
        }

        with self.assertRaises(InvalidDFA) as e:
            validate_transitions(self.states, transitions, self.alphabet)

        error = "A transition goes from an invalid state"

        self.assertTrue(error in str(e.exception))

    def test_invalid_to_state_in_transitions(self):
        transitions = {
            T(1, "a"): 100,
            T(1, "b"): 2,
            T(2, "a"): 3,
            T(2, "b"): 3,
            T(3, "a"): 4,
            T(3, "b"): 4,
            T(4, "a"): 1,
            T(4, "b"): 1,
        }

        with self.assertRaises(InvalidDFA) as e:
            validate_transitions(self.states, transitions, self.alphabet)

        error = "A transition goes to an invalid state"

        self.assertTrue(error in str(e.exception))

    def test_missing_transition(self):
        transitions = {
            T(1, "a"): 2,
            T(1, "b"): 2,
            T(2, "a"): 3,
            T(2, "b"): 3,
            T(3, "a"): 4,
            T(3, "b"): 4,
            T(4, "a"): 1,
            # Missing transition for state 4 on input "b"
        }

        with self.assertRaises(InvalidDFA) as e:
            validate_transitions(self.states, transitions, self.alphabet)

        error = "State '4' doesn't contain a transition for each character in the alphabet"

        self.assertTrue(error in str(e.exception))


class TestBasicDFA(unittest.TestCase):
    """A quick test to make sure DFAs can accept and reject strings"""
    def setUp(self):
        # Accepts a string with odd number of 'a's
        states = {1, 2}
        alphabet = {"a", "b"}
        final_states = {2}
        start_state = 1

        transitions = {
            T(1, "a"): 2,
            T(1, "b"): 1,
            T(2, "a"): 1,
            T(2, "b"): 2
        }

        self.dfa = DFA(states, alphabet, transitions, start_state, final_states)

        # sanity check
        validate_dfa(self.dfa)

    def test_accepts_string(self):
        input_string = "abbaa"

        self.assertTrue(dfa_accepts(self.dfa, input_string))

    def test_rejects_string(self):
        input_string = "abba"

        self.assertFalse(dfa_accepts(self.dfa, input_string))


class TestUnvalidatedInvalidDFA(unittest.TestCase):
    """
        Make sure dfa_accepts() nice error when something unexpected happens
        Shouldn't happen if the DFA has been put through the validator
    """
    def setUp(self):
        # Accepts a string with odd number of 'a's
        states = {1, 2}
        alphabet = {"a", "b"}
        final_states = {2}
        start_state = 1

        invalid_transitions = {
            T(1, "a"): 2,
            # Missing transition (1, "b)
            T(2, "a"): 1,
            T(2, "b"): 2
        }

        self.invalid_dfa = DFA(states, alphabet, invalid_transitions, start_state, final_states)

        # Intentionally don't validate the dfa

    # Throw error when a non-existant transition occurs
    # This shouldn't happen when the input character isn't in the alphabet
    #   - In this case it should just reject the string
    def test_throws_error(self):
        with self.assertRaises(InvalidDFA) as e:
            dfa_accepts(self.invalid_dfa, "bbbbb")

        error = "Something went wrong when attempting transition from state '1' on input 'b'"
        self.assertTrue(error in str(e.exception))


class TestInvalidInputString(unittest.TestCase):
    """Test that a valid DFA will reject on a character not in the alphabet"""
    def setUp(self):
        # Accepts a string with odd number of 'a's
        states = {1, 2}
        alphabet = {"a", "b"}
        final_states = {2}
        start_state = 1

        transitions = {
            T(1, "a"): 2,
            T(1, "b"): 1,
            T(2, "a"): 1,
            T(2, "b"): 2
        }

        self.dfa = DFA(states, alphabet, transitions, start_state, final_states)

        validate_dfa(self.dfa)

    # Input characters that aren't in the alphabet shouldn't error,
    # they should just be rejected by the DFA
    def test_rejects_string_with_unrecognized_character(self):
        self.assertFalse(dfa_accepts(self.dfa, "ababaQ"))


class TestDFAsAcceptAndReject(unittest.TestCase):
    def setUp(self):
        """
            Loads all the yaml files from the test_dfas folder and parses
            the DFAs they contain
        """
        yaml_docs = (load_yaml(filename) for filename in glob("test_dfas/*.yaml"))

        self.tests = [DFATest(doc, parse_dfa_from_yaml(doc)) for doc in yaml_docs]

        for test in self.tests:
            validate_dfa(test.dfa)

        self.MAX_GENERATED = 10000

    def test_dfas_with_generated_strings(self):
        """
            This test uses the exrex module to generate strings from a regular expression
            Each DFA yaml file includes it's own regular expression that describes the
            language.
        """
        for test in self.tests:
            # Take at most MAX_GENERATED strings from the exrex generator
            for input_string in take_from(exrex.generate(test.yaml["regex"]), self.MAX_GENERATED):
                # Run them through the DFA, raise exception if it doesn't accept
                if not dfa_accepts(test.dfa, input_string):
                    raise(UnexpectedRejection(test.yaml["description"], input_string, test.yaml["regex"]))

    def test_dfas_with_provided_strings(self):
        """
            Uses the strings provided in the Yaml files.
            Errors are raised if an accept string is rejected or a
            reject string is accepted
        """
        for test in self.tests:
            accept_strings = test.yaml["accept_strings"]
            reject_strings = test.yaml["reject_strings"]

            # Make sure there are actually strings defined
            self.assertTrue(len(accept_strings) > 0)
            self.assertTrue(len(reject_strings) > 0)

            for input_string in accept_strings:
                # Run them through the DFA, raise exception if it doesn't accept
                if not dfa_accepts(test.dfa, input_string):
                    raise(UnexpectedRejection(test.yaml["description"], input_string, test.yaml["regex"]))

            for input_string in reject_strings:
                # Run them through the DFA, raise exception if it accepts
                if dfa_accepts(test.dfa, input_string):
                    raise(UnexpectedAccept(test.yaml["description"], input_string, test.yaml["regex"]))
