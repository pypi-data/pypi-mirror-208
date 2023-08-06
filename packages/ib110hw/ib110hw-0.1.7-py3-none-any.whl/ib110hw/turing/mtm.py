from copy import deepcopy
from time import sleep
from typing import Dict, List, Optional, Set, Tuple, IO

from .base import BaseTuringMachine, MAX_STEPS_ERROR_MSG
from .tape import Direction, Tape, START_SYMBOL
from ._helpers import clear_console, close_file, mtm_config_to_md, get_step_direction

Symbols = Tuple[str, ...]
Directions = Tuple[Direction, ...]

MTMRule = Tuple[str, Symbols, Directions]
MTMRules = Dict[Symbols, MTMRule]
MTMTransitions = Dict[str, MTMRules]


class MTM(BaseTuringMachine):
    """
    Represents a Multi-tape Turing Machine
    """

    def __init__(
        self,
        states: Set[str] = None,
        input_alphabet: Set[str] = None,
        acc_state: str = "accept",
        rej_state: str = "reject",
        transitions: MTMTransitions = None,
        tape_count: int = 2,
        tapes: List[Tape] = None,
        initial_state: str = "init",
        start_symbol: str = START_SYMBOL,
    ):
        super().__init__(
            states,
            input_alphabet,
            acc_state,
            rej_state,
            initial_state,
            start_symbol,
        )
        self.transitions = transitions if transitions is not None else {}
        self.tapes = tapes or [deepcopy(Tape()) for _ in range(tape_count)]
        self.tape_count = tape_count or len(tapes)

    def get_transition(self, state: str, read: Symbols) -> Optional[MTMRule]:
        """
        Returns the transition based on the current state and read symbols.

        Args:
            state (str): Current state.
            read (Symbols): Current read symbols.

        Returns:
            Optional[MTMRule]: Transition based on the provided params if exists, None otherwise.
        """
        return self.transitions.get(state, {}).get(read, None)

    def write_to_tape(self, input_str: str, index: int = 0) -> None:
        """
        Writes the provided string on the tape on the index.

        Args:
            input_str (str): String to be written on the tape.
            index (int, optional): Index of the tape to be updated. Defaults to 0.
        """
        self.tapes[index].write(self.start_symbol + input_str)

    def clear_tape(self, index: int) -> None:
        """
        Clears the tape on the index.

        Args:
            index (int): Index of the tape.
        """
        self.tapes[index].clear()

    def clear_tapes(self) -> None:
        """
        Clears all the tapes
        """
        for tape in self.tapes:
            tape.clear()

    def read_tape(self, index: int = 0) -> str:
        """
        Reads contents of a tape by index.

        Returns:
            str: String written on the tape on index.
        """
        return self.tapes[index].read()

    def get_current_symbols(self) -> Symbols:
        """
        Gets the current symbols read by tape heads.

        Returns:
            Symbols: Symbols read by the tape heads.
        """
        return tuple((tape.current.value for tape in self.tapes))

    def simulate(
        self,
        to_console: bool = True,
        to_file: bool = False,
        path: str = "simulation.md",
        delay: float = 0.5,
        step_by_step: bool = False,
    ) -> bool:
        """Simulates the machine on its current tape configuration.

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
        steps: int = 1
        rule: Optional[MTMRule] = None
        output_file: Optional[IO] = open(path, "w") if to_file else None

        # key pressed by user when the 'step_by_step' is enabled, can be <left|right|esc>
        pressed_key: str = "right"
        prev_states: List[Tuple[str, List[Tape]]] = []

        def get_rule_string() -> str:
            """
            Parse the current configuration to string shown to user.
            """
            row = self.get_transition(state, self.get_current_symbols())
            step_index = steps if row else steps - 1
            next_step = f"{state}, {self.get_current_symbols()}"

            return f"{step_index}. ({next_step}) -> {row}"

        def write_machine_configuration() -> None:
            """
            Write the configuration string to all enabled outputs.
            """
            rule_str = get_rule_string()

            if output_file:
                output_file.write(mtm_config_to_md(self.tapes, rule_str))

            if to_console or step_by_step:
                clear_console()
                print(rule_str, "\n\n")

                for i, t in enumerate(self.tapes):
                    print(f"Tape {i}\n{t}")

                sleep(0 if step_by_step else delay)

        def go_forward() -> None:
            nonlocal rule, steps
            rule = self.get_transition(state, self.get_current_symbols())
            prev_states.append((state, deepcopy(self.tapes)))
            steps += 1

        def go_back() -> None:
            if not prev_states:
                return

            nonlocal steps, state
            steps -= 1
            state, self.tapes = prev_states.pop()

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

            state, write, directions = rule
            for direction, tape, symbol in zip(directions, self.tapes, write):
                tape.write_symbol(symbol)
                tape.move(direction)

        close_file(output_file)
        print(MAX_STEPS_ERROR_MSG.format(self.max_steps))

        return False


if __name__ == "__main__":
    pass
