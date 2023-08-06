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

from typing import Any, Dict, Iterable, List, Tuple

from comet_ml import utils


def prompt_call(
    input_model: str, input_messages: List[Dict[str, str]], output: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "type": "chat.completions",
        "timestamp": utils.local_timestamp(),
        "input": {"model": input_model, "messages": input_messages},
        "output": output,
    }


def prompt_choice_generator(
    messages: List[Dict[str, str]], choices: List[Dict[str, str]]
) -> Iterable[Tuple[str, str]]:
    prompt = "\n\n".join([_format_message(message) for message in messages])
    for choice in choices:
        yield (prompt, _format_message(choice))


def _format_message(message: Dict[str, str]) -> str:
    return "{}: {}".format(message["role"], message["content"])
