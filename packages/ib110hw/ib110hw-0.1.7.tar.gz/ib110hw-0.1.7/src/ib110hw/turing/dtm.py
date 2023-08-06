from copy import deepcopy
from time import sleep
from typing import Dict, Optional, Set, Tuple, List, IO

from .base import BaseTuringMachine, MAX_STEPS_ERROR_MSG
from .tape import Direction, Tape, START_SYMBOL
from ._helpers import dtm_config_to_md, clear_console, close_file, get_step_direction

DTMRule = Tuple[str, str, Direction]
DTMRules = Dict[str, DTMRule]
DTMTransitions = Dict[str, DTMRules]


class DTM(BaseTuringMachine):
    """
    Represents a Deterministic Turing Machine
    """

    def __init__(
        self,
        states: Set[str] = None,
        input_alphabet: Set[str] = None,
        acc_state: str = "accept",
        rej_state: str = "reject",
        transitions: DTMTransitions = None,
        tape: Tape = None,
        initial_state: str = "init",
        start_symbol: str = START_SYMBOL,
    ) -> None:
        super().__init__(
            states,
            input_alphabet,
            acc_state,
            rej_state,
            initial_state,
            start_symbol,
        )
        self.transitions = transitions if transitions is not None else {}
        self.tape = tape or Tape()

    def get_transition(self, state: str, read: str) -> Optional[DTMRule]:
        """
        Gets the transition based on the provided state and read symbol.

        Args:
            state (str): Current state of the DTM.
            read (str): Symbol read by the tape head.

        Returns:
            DTMRule: Transition based on the provided parms if exists, None otherwise.
        """
        return self.transitions.get(state, {}).get(read, None)

    def write_to_tape(self, input_str: str) -> None:
        """
        Writes the provided string on the tape.

        Args:
            input_str (str): String to be written on the tape.
        """
        self.tape.write(self.start_symbol + input_str)

    def clear_tape(self) -> None:
        """
        Clears the contents of the tape.
        """
        self.tape.clear()

    def read_tape(self) -> str:
        """
        Reads contents of the tape.

        Returns:
            str: String written on the tape.
        """
        return self.tape.read()

    def simulate(
        self,
        to_console: bool = True,
        to_file: bool = False,
        path: str = "simulation.md",
        delay: float = 0.5,
        step_by_step: bool = False,
    ) -> bool:
        """
        Simulates the machine on its current tape configuration.

        Args:
            to_console (bool, optional): Set to False if you only want to see the result. Defaults to True.
            to_file (bool, optional): Set to True if you want to save every step to the file. Defaults to False.
            path (str, optional): Path to the .md file with the step history. Defaults to "simulation.md".
            delay (float, optional): The delay (s) between each step when printing to console. Defaults to 0.5.
            step_by_step (bool, optional): Set to True if you want the simulation wait after each step. Defaults to False.

        Returns:
            bool: False if the machine rejects the word or exceeds the 'max_steps' value, True otherwise.
        """
        state: str = self.initial_state
        steps: int = 0
        rule: Optional[DTMRule] = None
        output_file: Optional[IO] = open(path, "w") if to_file else None

        # key pressed by user when the 'step_by_step' is enabled, can be <left|right|esc>
        pressed_key: str = "right"

        # remember the previous state and tape configuration to be able to go back and forth
        prev_states: List[Tuple[str, Tape]] = []

        def get_rule_string() -> str:
            """
            Parse the current configuration to string shown to user.
            """
            row = self.get_transition(state, self.tape.current.value)
            step_index = steps if row else steps - 1
            next_step = f"{state}, '{self.tape.current.value}'"

            return f"{step_index}. ({next_step}) -> {row}\n"

        def write_machine_configuration() -> None:
            """
            Write the configuration string to all enabled outputs.
            """
            rule_str = get_rule_string()

            if output_file:
                output_file.write(dtm_config_to_md(self.tape, rule_str))

            if to_console or step_by_step:
                clear_console()
                print(f"{rule_str}\n{self.tape}")
                sleep(0 if step_by_step else delay)

        def go_forward() -> None:
            """
            Goes one step forward in the computation.
            """
            nonlocal steps, rule, prev_states
            rule = self.get_transition(state, self.tape.current.value)
            prev_states.append((state, deepcopy(self.tape)))
            steps += 1

        def go_back() -> None:
            """
            Goes one step back in the computation.
            Does nothing if there is no previous step.
            """
            if not prev_states:
                return

            nonlocal steps, state
            steps -= 1
            state, self.tape = prev_states.pop()

        while steps <= (self.max_steps + 1):
            write_machine_configuration()

            if state == self.acc_state:
                close_file(output_file)
                return True

            if step_by_step:
                pressed_key = get_step_direction()

            if pressed_key == "esc":
                close_file(output_file)
                print("Canceled the computation.")
                return False

            if pressed_key == "left":
                go_back()
                continue

            go_forward()

            if not rule or rule[0] == self.rej_state:
                close_file(output_file)
                return False

            state, write, direction = rule
            self.tape.write_symbol(write)
            self.tape.move(direction)

        close_file(output_file)
        print(MAX_STEPS_ERROR_MSG.format(self.max_steps))

        return False


if __name__ == "__main__":
    pass
