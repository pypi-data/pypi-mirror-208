from typing import Set


class BaseFiniteAutomaton:
    """
    Represents an abstract Finite Automaton class. This class cannot be instantiated.
    """

    def __new__(cls, *args, **kwargs):
        if cls is BaseFiniteAutomaton:
            raise TypeError("Only NFA and DFA can be instantiated!")

        return object.__new__(cls)

    def __init__(
        self,
        states: Set[str] = None,
        alphabet: Set[str] = None,
        initial_state: str = None,
        final_states: Set[str] = None,
    ) -> None:
        self.states = states if states is not None else set()
        self.alphabet = alphabet if alphabet is not None else set()
        self.initial_state = initial_state
        self.final_states = final_states if final_states is not None else set()

    def __repr__(self) -> str:
        alphabet_str = f"alphabet: {','.join(sorted(self.alphabet))}"
        states_str = f"states: {','.join(sorted(self.states))}"
        initial_str = f"initial state: {self.initial_state}"
        final_states_str = f"final states: {','.join(sorted(self.final_states))}"

        return f"{alphabet_str}\n{states_str}\n{initial_str}\n{final_states_str}\n"

    def __repr_row_prefix__(self, state: str):
        if state == self.initial_state:
            return "<-> " if state in self.final_states else "--> "

        return "<-- " if state in self.final_states else "    "

    def add_state(self, state: str, is_final: bool = False) -> bool:
        if state in self.states:
            return False

        if is_final:
            self.final_states.add(state)

        self.states.add(state)

        return True

    def remove_state(self, state) -> bool:
        if state not in self.states:
            return False

        if state in self.final_states:
            self.final_states.remove(state)

        self.states.difference_update({state})

        return True

    def is_valid(self) -> bool:
        return (
            self.states
            and self.initial_state in self.states
            and self.final_states.issubset(self.states)
        )

    def complement(self) -> None:
        """
        Complements the automaton. (Final states will become non-final and vice-versa).
        """
        self.final_states = self.states - self.final_states


if __name__ == "__main__":
    pass
