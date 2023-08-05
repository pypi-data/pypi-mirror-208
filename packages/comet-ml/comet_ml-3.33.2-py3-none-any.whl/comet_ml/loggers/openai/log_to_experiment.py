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

import importlib
import io
import json
from typing import TYPE_CHECKING, Any, Dict, Iterator, Tuple

from comet_ml import event_tracker

from . import session_registry

if TYPE_CHECKING:  # pragma: no cover
    import comet_ml


def token_metrics(
    experiment: "comet_ml.Experiment", usage: Dict[str, Any], step: int
) -> None:
    for token_key in ["prompt_tokens", "completion_tokens", "total_tokens"]:
        used_amount = session_registry.accumulate_and_get(
            experiment.id, token_key, usage[token_key]
        )
        experiment.__internal_api__log_metric__(
            "openai_{}".format(token_key), used_amount, step=step, framework="openai"
        )


def accumulated_prompt_calls(
    experiment: "comet_ml.Experiment", prompt_call: Dict[str, Any]
) -> None:
    session_prompt_calls = session_registry.accumulate_and_get(
        experiment.id, "prompt_calls", [prompt_call]
    )
    experiment.log_asset(
        io.StringIO(json.dumps(session_prompt_calls)),
        file_name="openai-prompts.json",
        overwrite=True,
    )


def texts(
    experiment: "comet_ml.Experiment",
    prompts_choices: Iterator[Tuple[str, str]],
    step: int,
) -> None:
    for prompt, choice in prompts_choices:
        experiment.log_text(prompt, metadata={"choice": choice}, step=step)


def user_config(experiment: "comet_ml.Experiment") -> None:
    if event_tracker.is_registered("openai_user_config_logged", experiment.id):
        return

    openai = importlib.import_module("openai")

    experiment.log_other("openai_organization", openai.organization)
    experiment.log_other("openai_api_base", openai.api_base)
    experiment.log_other("openai_api_type", openai.api_type)

    event_tracker.register("openai_user_config_logged", experiment.id)


def call_status(experiment: "comet_ml.Experiment", is_error: bool, step: int) -> None:
    accumulated_errors = session_registry.accumulate_and_get(
        experiment.id, "openai_errors", int(is_error)
    )
    if accumulated_errors > 0:
        experiment.__internal_api__log_metric__(
            "openai_errors", accumulated_errors, step=step, framework="openai"
        )
