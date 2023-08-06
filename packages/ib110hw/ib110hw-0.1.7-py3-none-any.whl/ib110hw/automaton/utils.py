from typing import Union
from .nfa import NFA
from .dfa import DFA


def automaton_to_graphviz(automaton: Union[NFA, DFA], path: str) -> None:
    """
    Converts automaton to the graphviz format (.dot file) and saves
    the result in the specified location.

    Args:
        automaton (Union[NFA, DFA]): Automaton to be converted.
        path (str): Path where the file will be created.
    """
    with open(path, "w", encoding="utf-8") as file:
        file.write("digraph G {\n")
        file.write('\trankdir="LR"\n')
        file.write('\t__init__[shape=none label=""]\n')
        file.write(f"\t__init__ -> {automaton.initial_state}\n")

        for s_from in automaton.states:
            for s_to in automaton.states:
                label_symbols = automaton.get_symbols_between_states(s_from, s_to)
                if "" in label_symbols:
                    label_symbols.discard("")
                    label_symbols.add("ε")

                label = ",".join(label_symbols)
                if label:
                    file.write(f'\t{s_from} -> {s_to}[label="{label}"]\n')

        for non_fin_state in automaton.states.difference(automaton.final_states):
            file.write(f"\t{non_fin_state} [shape=circle]\n")

        for fin_state in automaton.final_states:
            file.write(f"\t{fin_state} [shape=doublecircle]\n")

        file.write("}\n")


if __name__ == "__main__":
    pass
