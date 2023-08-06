from os import name, system
from typing import IO, List, Tuple, Set, Optional, Callable
from .tape import Tape, Direction
from itertools import takewhile, dropwhile
from pynput import keyboard
import re


def clear_console() -> None:
    if name == "posix":
        system("clear")
    else:
        system("cls")


def close_file(file: IO) -> None:
    if file:
        file.close()


# inspired by https://stackoverflow.com/a/43106497
def get_step_direction() -> str:
    step_direction = None
    print("Use arrow keys [L|R] to go back or forward. Press ESC to exit.")

    def on_press(key):
        nonlocal step_direction
        try:
            if key.name in ["left", "right", "esc"]:
                step_direction = key.name
                return False
        except AttributeError:
            # ignore other keys
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()
    return step_direction


def tape_to_md(tape: Tape, index: int = None) -> str:
    index_str = "" if index is None else f"<b>Tape {index}:</b>"
    tape_str = f"{tape}".replace("^", "<b>^</b>")
    return f"{index_str}\n{tape_str}\n"


def rule_to_md(rule_str: str) -> str:
    return f"######{rule_str.replace('->', '&rarr;')}"


def dtm_config_to_md(tape: Tape, rule_str: str) -> str:
    header_str = rule_to_md(rule_str)
    tape_str = tape_to_md(tape)

    return f"{header_str}\n<pre>\n{tape_str}</pre>\n---\n"


def mtm_config_to_md(tapes: List[Tape], rule_str: str) -> str:
    header_str = rule_to_md(rule_str)
    tapes_str = "".join(tape_to_md(tape, i) for i, tape in enumerate(tapes))

    return f"{header_str}\n<pre>\n{tapes_str}</pre>\n---\n"


def read_file(file_path: str) -> List[str]:
    result = []
    with open(file_path, "r") as in_file:
        for line in in_file:
            line = " ".join(line.split())

            if not line.strip() or line.startswith("#"):
                continue

            result.append(f"{line.strip()}")

    return result


def parse_direction(direction: str) -> Optional[Direction]:
    directions = {"L": -1, "R": 1, "S": 0}
    return Direction(directions.get(direction, 0))


def get_dtm_configuration(
    definition: List[str],
) -> Tuple[str, str, str, Set[str]]:
    config = list(takewhile(lambda l: l.strip() != "---", definition))[:-1]
    init, acc, rej = "", "", ""
    alphabet = set()

    for line in config:
        if line.startswith("init"):
            init = line.split()[1]
        elif line.startswith("acc"):
            acc = line.split()[1]
        elif line.startswith("rej"):
            rej = line.split()[1]
        elif line.startswith("alphabet"):
            alphabet = {*line.split()[1:]}

    return init, acc, rej, alphabet or set()


def get_mtm_configuration(
    definition: List[str],
) -> Tuple[str, str, str, Set[str], int]:
    config = next(
        (
            idk
            for idk in list(takewhile(lambda l: l.strip() != "---", definition))
            if idk.strip().startswith("tapes")
        )
    )
    tape_count = int(config.split()[1])

    return (*get_dtm_configuration(definition), tape_count)


def get_dtm_transition_function(definition: List[str]):
    function_lines = list(dropwhile(lambda l: l != "---", definition))[1:]
    function = {}

    for rule in function_lines:
        left, right = rule.split("->")
        curr_state, read = left.split()
        next_state, write, direction = right.split()

        if not function.get(curr_state):
            function[curr_state] = {}

        read = read if read != "_" else ""
        write = write if write != "_" else ""
        function[curr_state][read] = (next_state, write, parse_direction(direction))

    return function


def validate_dtm_configuration(definition: List[str]) -> Optional[str]:
    if all(l.strip() != "---" for l in definition):
        return "The divider is missing."

    config = list(takewhile(lambda l: l != "---", definition))

    if not any((l.startswith("init") for l in config)):
        return "Specifying the initial state is mandatory."

    init_line = next((l for l in config if l.startswith("init")), None)
    if init_line and len(init_line.split()) != 2:
        return "Invalid initial state."

    acc_line = next((l for l in config if l.startswith("acc")), None)
    if acc_line and len(acc_line.split()) != 2:
        return "Invalid accepting state."

    rej_line = next((l for l in config if l.startswith("rej")), None)
    if rej_line and len(rej_line.split()) != 2:
        return "Invalid rejecting state."

    alphabet_line = next((l for l in config if l.startswith("alphabet")), None)
    if not alphabet_line:
        return "The alphabet definition is missing."

    if len(alphabet_line.split()) < 2 or any(len(s) > 1 for s in alphabet_line.split()[1:]):
        return "Invalid alphabet."


def validate_mtm_configuration(definition: List[str]) -> Optional[str]:
    err = validate_dtm_configuration(definition)
    if err:
        return err

    tapes_line = [
        l for l in definition if re.match(r"tapes ([2-9]|[1-9]\d+)", l.strip())
    ]
    if len(tapes_line) > 1:
        return "Duplicate definition of tape count."

    if not tapes_line:
        return "Missing or invalid definition of tape count."


def validate_dtm_transitions(definition: List[str]) -> Optional[str]:
    get_part = lambda l, i: l.split("->")[i]
    
    # checks the length of arguments on the left side
    valid_current = lambda l: len(get_part(l, 0).split()) == 2
    
    # checks the length of the read symbol
    valid_read = lambda l: len(get_part(l, 0).split()[1]) == 1
    
    # checks the length of arguments on the right side
    valid_next = lambda l: len(get_part(l, 1).split()) == 3
    
    # checks the length of the write symbol
    valid_write = lambda l: len(get_part(l, 1).split()[1]) == 1
    
    # checks the direction
    valid_dir = lambda l: get_part(l, 1).split()[-1] in ["L", "R", "S"]

    return validate_transitions(
        definition,
        valid_current,
        valid_read,
        valid_next,
        valid_write,
        valid_dir,
    )


def validate_mtm_transitions(definition: List[str]) -> Optional[str]:
    get_part = lambda l, i: l.split("->")[i]
    # checks the length of arguments on the left side
    valid_current = lambda l: re.match(r"^\w+ \([^)]+\)", get_part(l, 0)) is not None
    
    # checks the length of the read symbols
    valid_read = (
        lambda l: re.match(r"(. )+.", get_part(l, 0).split(" (")[1][:-1]) is not None
    )
    # checks the length of arguments on the right side
    valid_next = lambda l: len(list(filter(None, get_part(l, 1).split(" (")))) == 3
    
    # checks the length of the write symbols
    valid_write = (
        lambda l: bool(re.match(r"^(. )+.$", get_part(l, 1).split(" (")[1][:-1])) == 1
    )
    
    # checks the direction
    valid_dir = lambda l: set(get_part(l, 1).split(" (")[-1][:-1].split()).issubset(
        ["L", "R", "S"]
    )

    return validate_transitions(
        definition,
        valid_current,
        valid_read,
        valid_next,
        valid_write,
        valid_dir,
    )


def validate_transitions(
    definition: List[str],
    valid_current: Callable[[str], bool],
    valid_read: Callable[[str], bool],
    valid_next: Callable[[str], bool],
    valid_write: Callable[[str], bool],
    valid_dir: Callable[[str], bool],
) -> Optional[str]:

    for line in list(dropwhile(lambda l: l != "---", definition))[1:]:
        if "->" not in line:
            return f"Missing arrow in rule:\n{line}."

        if not valid_current(line):
            return f"Invalid combination of state and read symbol in rule:\n{line}"

        if not valid_read(line):
            return f"Invalid read symbol length (> 1) in rule:\n{line}"

        if not valid_next(line):
            return (
                f"The next state, write symbol or direction is missing in rule:\n{line}"
            )

        if not valid_write(line):
            return f"Invalid write symbol length (> 1) in rule:\n{line}"

        if not valid_dir(line):
            return f"Invalid direction in rule:\n{line}"


def get_mtm_transition_function(definition: List[str]):
    function_lines = list(dropwhile(lambda l: l != "---", definition))[1:]
    function = {}

    def clean(group: str) -> List[str]:
        """Removes brackets and spaces + returns as list."""
        return re.sub(r"[()]", "", group).split()

    def underscore_to_space(group: List[str]) -> List[str]:
        return [s if s != "_" else "" for s in group]

    for rule in function_lines:
        left, right = rule.split("->")
        curr_state, reads = left.split(" ", 1)
        next_state, writes, directions = right.split("(")

        if not function.get(curr_state):
            function[curr_state] = {}

        function[curr_state][tuple(underscore_to_space(clean(reads)))] = (
            next_state.strip(),
            tuple(underscore_to_space(clean(writes))),
            tuple(parse_direction(d) for d in clean(directions)),
        )

    return function


if __name__ == "__main__":
    pass
