from exrex import generate
from hypothesis.strategies import integers, composite, DrawFn, lists, sampled_from
from ib110hw.automaton.dfa import DFA
from ib110hw.automaton.nfa import NFA
from itertools import islice
from typing import Set


@composite
def states(draw: DrawFn, min_states: int, max_states: int):
    """
    Composite strategy to generate automaton states with name formatted as 's' + index.

    Args:
        min_states (int): The minimum amount of states.
        max_states (int): The maximum amount of states.
    """
    return [
        f"s{i}"
        for i in range(draw(integers(min_value=min_states, max_value=max_states)))
    ]


@composite
def dfas(
    draw: DrawFn,
    alphabet: Set[str],
    min_states: int = 5,
    max_states: int = 10,
    min_fin_states: int = 1,
    max_fin_states: int = 10,
):
    """
    Composite strategy to generate random DFA based on the provided params.

    Args:
        alphabet (Set[str]): Alphabet of the automaton.
        min_states (int, optional): The minimum amount of states. Defaults to 5.
        max_states (int, optional): The maximum amount of states. Defaults to 10.
        min_fin_states (int, optional): The minimum amount of final states. Defaults to 1.
        max_fin_states (int, optional): The maximum amount of final states. Defaults to 10.
    """

    def add_next_states(_state: str) -> None:
        next_states = draw(
            lists(
                sampled_from(automaton_states),
                min_size=len(alphabet),
                max_size=len(alphabet),
            )
        )

        for next_s, symbol in zip(next_states, alphabet):
            automaton.add_transition(_state, next_s, symbol)

    automaton_states = draw(states(min_states, max_states))
    min_fin_size = min(len(automaton_states), min_fin_states)
    max_fin_size = min(len(automaton_states), max_fin_states)
    automaton = DFA(
        set(automaton_states),
        alphabet,
        draw(sampled_from(automaton_states)),
        set(
            draw(
                lists(
                    sampled_from(automaton_states),
                    min_size=min_fin_size,
                    max_size=max_fin_size,
                )
            )
        ),
        {},
    )

    add_next_states(automaton.initial_state)

    for state in automaton.states.difference([automaton.initial_state]):
        add_next_states(state)

    return automaton


@composite
def nfas(
    draw: DrawFn,
    alphabet: Set[str],
    min_deg: int = 1,
    max_deg: int = None,
    min_states: int = 5,
    max_states: int = 10,
    min_fin_states: int = 1,
    max_fin_states: int = 10,
):
    """
    Composite strategy to generate random DFA based on the provided params.

    Args:
        alphabet (Set[str]): Alphabet of the automaton.
        min_deg (int): The minimum amount of transitions from this state. Defaults to 1.
        max_deg (int): The maximum amount of transitions from this state. Defaults to the amount of states.
        min_states (int, optional): The minimum amount of states. Defaults to 5.
        max_states (int, optional): The maximum amount of states. Defaults to 10.
        min_fin_states (int, optional): The minimum amount of final states. Defaults to 1.
        max_fin_states (int, optional): The maximum amount of final states. Defaults to 10.
    """

    def add_next_states(_min_deg: int, _max_deg: int, _state: str) -> None:
        s_deg = integers(_min_deg, _max_deg)
        next_states = draw(
            lists(
                sampled_from(states), min_size=min(s_deg, len(states)), max_size=max_deg
            )
        )

        for next_state in next_states:
            symbol = draw(sampled_from(alphabet))
            automaton.add_transition(_state, {next_state}, symbol)

    automaton_states = draw(states(min_states, max_states))
    min_fin_size = min(len(automaton_states), min_fin_states)
    max_fin_size = min(len(automaton_states), max_fin_states)
    automaton = NFA(
        set(states),
        alphabet,
        draw(sampled_from(states)),
        set(
            draw(
                lists(
                    sampled_from(automaton_states),
                    min_size=min_fin_size,
                    max_size=max_fin_size,
                )
            )
        ),
        {},
    )

    if not (max_deg) or max_deg > len(automaton_states):
        max_deg = len(automaton_states)

    add_next_states(1, max_deg, automaton.initial_state)

    for state in automaton.states.difference([automaton.initial_state]):
        add_next_states(min_deg, max_deg, state)

    return automaton


@composite
def strings_from_regex(
    draw: DrawFn,
    regex: str,
    min_amount: int = 5,
    max_amount: int = 10,
    max_str_len: int = 5,
):
    """
    Composite strategy to generate strings based on the provided regular expression.

    Args:
        regex (str): Regular expression used to generate strings.
        min_amount (int, optional): Min amount of strings to be generated. Defaults to 5.
        max_amount (int, optional): Max amount of strings to be generated. Defaults to 10.
        max_str_len (int, optional): Max length of individual generated strings. Defaults to 5.
    """
    amount = draw(integers(min_value=min_amount, max_value=max_amount))
    generator = islice(generate(regex, limit=max_str_len), amount)

    return set(generator)


if __name__ == "__main__":
    pass
