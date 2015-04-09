import unittest
from collections import namedtuple

from DFA import DFA
from DFA import validate_dfa
from DFA import dfa_accepts
from DFA import validate_final_states
from DFA import validate_start_state
from DFA import validate_transitions
from DFA import InvalidDFA

# Convenience class so that I can reference the parameters to the
# transition function by name
#
# tuple of state -> character
T = namedtuple("transition_key", ["state", "character"])


class TestDfa_StartState_FinalStates(unittest.TestCase):
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

        error = "A transition uses a character that's not in the DFA's alphabet"

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
