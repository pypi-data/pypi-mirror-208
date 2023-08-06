from sys import path
from hypothesis import given, assume
from hypothesis.strategies import integers, sets, characters, composite, DrawFn
from tests.generation import r_dfa
from random import choice

path.append("../src/ib110hw")

from automaton.dfa import DFA


@composite
def r_test_dfa(
    draw: DrawFn,
    min_deg=integers(min_value=1, max_value=10),
    max_deg=integers(min_value=1, max_value=10),
    min_states=integers(min_value=3, max_value=10),
    max_states=integers(min_value=3, max_value=10),
    min_fin_states=integers(min_value=1, max_value=10),
    max_fin_states=integers(min_value=2, max_value=10),
    alphabet=sets(characters(), min_size=2, max_size=20),
):
    max_deg = draw(max_deg)
    min_deg = min(draw(min_deg), max_deg)
    max_states = draw(max_states)
    min_states = min(draw(min_states), max_states)
    max_fin_states = draw(max_fin_states)
    min_fin_states = min(draw(min_fin_states), max_fin_states)

    r_automaton = r_dfa(
        min_deg,
        max_deg,
        min_states,
        max_states,
        min_fin_states,
        max_fin_states,
        draw(alphabet),
    )

    diff = r_automaton.states.difference(r_automaton.final_states)
    assume(diff and diff != {r_automaton.initial_state})

    return r_automaton


@given(r_test_dfa())
def test_add_state(automaton: DFA) -> None:
    assert automaton.add_state("test_state_1")
    # cannot add the same state twice
    assert not automaton.add_state("test_state_1")
    assert not automaton.add_state("test_state_1", True)

    assert "test_state_1" in automaton.states
    assert "test_state_1" not in automaton.final_states
    assert "test_state_1" not in automaton.transitions

    assert automaton.add_state("test_state_2", True)
    assert not automaton.add_state("test_state_2")
    assert "test_state_2" in automaton.states
    assert "test_state_2" in automaton.final_states


@given(r_test_dfa())
def test_remove_state(automaton: DFA):
    state_to_remove = choice(
        [s for s in automaton.states if s not in automaton.final_states]
    )

    assert automaton.remove_state(state_to_remove)
    # cannot remove the same state twice
    assert not automaton.remove_state(state_to_remove)
    assert state_to_remove not in automaton.states
    assert not automaton.remove_state("not_existent")

    state_to_remove = choice(list(automaton.final_states))

    assert automaton.remove_state(state_to_remove)
    assert state_to_remove not in automaton.states
    assert state_to_remove not in automaton.final_states
    assert not automaton.transitions.get(state_to_remove, None)


@given(r_test_dfa())
def test_add_transition(automaton: DFA) -> None:
    assert automaton.add_transition("test_state", "test_state", "a")
    assert "test_state" in automaton.transitions.keys()
    assert "a" in automaton.transitions["test_state"].keys()
    assert "test_state" == automaton.transitions["test_state"]["a"]
    assert not automaton.add_transition("test_state", "test_state", "a")


@given(r_test_dfa())
def test_set_transition(automaton: DFA) -> None:
    automaton.set_transition("s_from", "s_to", "symbol")
    assert automaton.get_transition("s_from", "symbol") == "s_to"

    automaton.set_transition("s_from", "s_to2", "symbol2")
    assert automaton.get_transition("s_from", "symbol2") == "s_to2"
    assert automaton.get_transition("s_from", "symbol") == "s_to"

    automaton.set_transition("s_from", "s_to2", "symbol")
    assert automaton.get_transition("s_from", "symbol") == "s_to2"


@given(r_test_dfa())
def test_remove_transition(automaton: DFA) -> None:
    automaton.add_state("test_state")
    automaton.alphabet.add("a")
    automaton.add_transition("test_state", automaton.initial_state, "a")

    assert not automaton.remove_transition("test_state", "not_exists")
    assert not automaton.remove_transition(
        "test_state", automaton.alphabet.difference(["a"]).pop()
    )
    assert not automaton.remove_transition("not_exists", "a")
    assert automaton.remove_transition("test_state", "a")
    assert not automaton.get_transition("test_state", "a")


def test_is_accepted() -> None:
    automaton: DFA = DFA(
        states={"s0", "s1", "s2", "s3", "s4"},
        alphabet={"a", "b", "c"},
        initial_state="s0",
        final_states={"s0", "s3"},
        transitions={
            "s0": {"a": "s0", "b": "s0", "c": "s1"},
            "s1": {"a": "s4", "b": "s2", "c": "s1"},
            "s2": {"a": "s3", "b": "s1", "c": "s1"},
            "s3": {"a": "s3", "b": "s3", "c": "s2"},
            "s4": {"a": "s4", "b": "s4", "c": "s4"},
        },
    )

    # words accepted in s0
    acc_s0 = ["", "a", "b", "ab", "aba", "abba"]
    # words accepted in s3 (starting from s1)
    acc_s3 = ["ba", "cbaab", "cbaca", "bbba", "bcba", "baccbab"]
    # words accepted in s0 and s1 (starting from s0)
    acc = [f"{w0}c{w1}" for w0 in acc_s0 for w1 in acc_s3] + acc_s0

    for acc_str in acc:
        assert automaton.is_accepted(acc_str)

    # words rejected in s1
    rej_s1 = ["c", "cc", "cbb", "cbc", "cbb", "cbbc"]
    # words rejected in s2 (starting from s1)
    rej_s2 = ["b", "bbc", "bac", "baac", "babc", "baccb"]
    # words rejected in s4
    rej_s4 = [f"{w}a" for w in rej_s1]
    # words rejected in s1, s2 and s4 (starting from s0)
    rej = [
        f"{w}{w4}"
        for w in [f"{w1}{w2}" for w1 in rej_s1 for w2 in rej_s2]
        for w4 in rej_s4
    ] + rej_s1

    for rej_str in rej:
        assert not automaton.is_accepted(rej_str)


def test_is_valid() -> None:
    automaton: DFA = DFA(
        states={"s0", "s1", "s2"},
        alphabet={"a", "b", "c"},
        initial_state="s0",
        final_states={"s1", "s2"},
        transitions={
            "s0": {"a": "s0", "b": "s2", "c": "s1"},
            "s1": {"a": "s1", "b": "s1", "c": "s2"},
            "s2": {"a": "s1", "b": "s0", "c": "s1"},
        },
    )

    assert automaton.is_valid()

    # invalid initial state
    automaton.initial_state = "s3"
    assert not automaton.is_valid()

    automaton.initial_state = "s0"
    assert automaton.is_valid()

    # invalid state in the transition function
    automaton.set_transition("s0", "s3", "c")
    assert not automaton.is_valid()

    automaton.set_transition("s0", "s1", "c")
    assert automaton.is_valid()

    # final states set is not subset of the states set
    automaton.final_states.update({"s3"})
    assert not automaton.is_valid()

    automaton.final_states.remove("s3")
    assert automaton.is_valid()

    # invalid character in the transition function
    automaton.add_transition("s0", "s1", "x")
    assert not automaton.is_valid()

    automaton.remove_transition("s0", "x")
    assert automaton.is_valid()

    # transition function is not total
    automaton.remove_transition("s0", "c")
    assert not automaton.is_valid()

    automaton.add_transition("s0", "s1", "c")
    assert automaton.is_valid()

    # empty states set
    automaton.states = set()
    assert not automaton.is_valid()
