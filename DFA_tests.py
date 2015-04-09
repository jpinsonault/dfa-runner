import unittest
from DFA import DFA
from DFA import validate_dfa
from DFA import validate_final_states
from DFA import validate_start_state
from DFA import validate_transitions
from DFA import InvalidDFA
from DFA import T


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

        expected_error_message = "Accepting states should be in the list of states"
        self.assertTrue(expected_error_message in str(e.exception))

    def test_invalid_final_state_with_valid_state(self):
        with self.assertRaises(InvalidDFA) as e:
            # 1 is in states, 6 is not
            final_states = {1, 6}

            validate_final_states(self.states, final_states)

        expected_error_message = "Accepting states should be in the list of states"
        self.assertTrue(expected_error_message in str(e.exception))

    def test_valid_start_state(self):
        start_state = 1

        validate_start_state(self.states, start_state)

    def test_invalid_start_state(self):
        # 1 is in states, 6 is not
        start_state = 6

        with self.assertRaises(InvalidDFA) as e:
            validate_start_state(self.states, start_state)

        expected_error_message = "Start state should be in the list of states"
        self.assertTrue(expected_error_message in str(e.exception))


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

        expected_error_message = "A transition uses a character that's not in the DFA's alphabet"

        self.assertTrue(expected_error_message in str(e.exception), str(e.exception))

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

        expected_error_message = "A transition goes from an invalid state"

        self.assertTrue(expected_error_message in str(e.exception))

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

        expected_error_message = "A transition goes to an invalid state"

        self.assertTrue(expected_error_message in str(e.exception))

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

        expected_error_message = "State '4' doesn't contain a transition for each character in the alphabet"

        self.assertTrue(expected_error_message in str(e.exception))
