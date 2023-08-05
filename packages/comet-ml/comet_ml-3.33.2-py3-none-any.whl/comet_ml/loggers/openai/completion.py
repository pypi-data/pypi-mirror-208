# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

from typing import Any, Dict, Iterable, Iterator, List, Tuple

from comet_ml import utils


def prompt_choice_generator(
    prompt: Any, choices: List[str]
) -> Iterator[Tuple[str, str]]:
    prompt = _prompt_to_strings(prompt)

    if len(prompt) != 0:
        choices_per_prompt = len(choices) // len(prompt)

    for prompt_index, prompt_entry in enumerate(prompt):
        for i in range(choices_per_prompt):
            choice = choices[prompt_index * choices_per_prompt + i]
            yield (prompt_entry, choice)


def _prompt_to_strings(prompt: Any) -> List[str]:
    """
    "a" -> ["a"]
    ["a", "b"] -> ["a", "b"]
    [1, 2, 3] -> ["[1, 2, 3]"]
    [[1, 2], [3, 4]] -> ["[1, 2]", "[3, 4]"]

    Anything else -> []
    """
    if isinstance(prompt, str):
        return [prompt]

    if not isinstance(prompt, list):
        return []

    if len(prompt) == 0:
        return prompt

    if _all_of_type(prompt, str):
        return prompt

    if _all_of_type(prompt, int):
        return [str(prompt)]

    if all(_all_of_type(entry, int) for entry in prompt):
        return [str(entry) for entry in prompt]

    return []


def _all_of_type(collection: Iterable, type_: type) -> bool:
    return all(isinstance(entry, type_) for entry in collection)


def prompt_call(
    input_model: str, input_prompt: str, output: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "type": "completions",
        "timestamp": utils.local_timestamp(),
        "input": {"model": input_model, "prompt": input_prompt},
        "output": output,
    }
