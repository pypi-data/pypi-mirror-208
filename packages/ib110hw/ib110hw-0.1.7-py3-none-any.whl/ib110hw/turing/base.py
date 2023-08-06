from typing import Set

MAX_STEPS_ERROR_MSG = """
Exceeded the maximum allowed steps. ({})
You change the default value by setting the 'max_steps' property of this automaton."""


class BaseTuringMachine:
    """Represents an abstract Turing machine class. This class cannot be instantiated."""

    def __new__(cls, *args, **kwargs):
        if cls is BaseTuringMachine:
            raise TypeError("Only DTM and MTM can be instantiated!")

        return object.__new__(cls)

    def __init__(
        self,
        states: Set[str],
        input_alphabet: Set[str],
        acc_state: str = "accept",
        rej_state: str = "reject",
        initial_state: str = "init",
        start_symbol: str = ">",
    ) -> None:
        self.states = states or set()
        self.input_alphabet = input_alphabet or set()
        self.acc_state = acc_state
        self.rej_state = rej_state
        self.initial_state = initial_state
        self.start_symbol = start_symbol

        # After exceeding max_steps value, the turing machine will be considered as looping.
        # Change this value for more complex scenarios.
        self.max_steps = 100


if __name__ == "__main__":
    pass
