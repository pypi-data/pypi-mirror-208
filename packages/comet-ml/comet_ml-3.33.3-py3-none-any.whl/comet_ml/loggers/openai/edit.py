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

from typing import Any, Dict, Iterator, List, Tuple

from comet_ml import utils


def prompt_choice_generator(
    text: str, instruction: str, choices: List[str]
) -> Iterator[Tuple[str, str]]:
    for choice in choices:
        yield ("Input: {}\n\nInstruction: {}".format(text, instruction), choice)


def prompt_call(
    input_model: str, input_text: str, input_instruction: str, output: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "type": "edits",
        "timestamp": utils.local_timestamp(),
        "input": {
            "model": input_model,
            "input": input_text,
            "instruction": input_instruction,
        },
        "output": output,
    }
