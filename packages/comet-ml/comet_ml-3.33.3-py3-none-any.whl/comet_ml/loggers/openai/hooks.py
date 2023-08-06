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

import logging
from typing import TYPE_CHECKING, Any, Dict, Iterator, Tuple

from comet_ml import event_tracker, monkey_patching

import box

from . import chat_completion, completion, edit, log_to_experiment, session_registry

if TYPE_CHECKING:  # pragma: no cover
    import comet_ml

LOGGER = logging.getLogger(__name__)


def completion_create(experiment, original, return_value, *args, **kwargs):
    if not _autologging_enabled(experiment, kwargs):
        return

    session_step = session_registry.accumulate_and_get(experiment.id, "step", 1)

    if _processed_call_status(experiment, return_value, session_step).is_error:
        return

    prompt, model = kwargs["prompt"], kwargs["model"]

    choices = [choice["text"] for choice in return_value["choices"]]
    prompt_call = completion.prompt_call(model, prompt, return_value)
    prompts_choices = completion.prompt_choice_generator(prompt, choices)
    token_usage = return_value["usage"]

    _log(experiment, prompts_choices, prompt_call, token_usage, session_step)


def chat_completion_create(experiment, original, return_value, *args, **kwargs):
    if not _autologging_enabled(experiment, kwargs):
        return

    session_step = session_registry.accumulate_and_get(experiment.id, "step", 1)
    if _processed_call_status(experiment, return_value, session_step).is_error:
        return

    prompt, model = kwargs["messages"], kwargs["model"]

    choices = [choice["message"] for choice in return_value["choices"]]
    prompt_call = chat_completion.prompt_call(model, prompt, return_value)
    prompts_choices = chat_completion.prompt_choice_generator(prompt, choices)
    token_usage = return_value["usage"]

    _log(experiment, prompts_choices, prompt_call, token_usage, session_step)


def edit_create(experiment, original, return_value, *args, **kwargs):
    if not experiment.auto_metric_logging:
        return

    session_step = session_registry.accumulate_and_get(experiment.id, "step", 1)

    if _processed_call_status(experiment, return_value, session_step).is_error:
        return

    input_text, instruction, model = (
        kwargs["input"],
        kwargs["instruction"],
        kwargs["model"],
    )

    choices = [choice["text"] for choice in return_value["choices"]]
    prompt_call = edit.prompt_call(model, input_text, instruction, return_value)
    prompts_choices = edit.prompt_choice_generator(input_text, instruction, choices)
    token_usage = return_value["usage"]

    _log(experiment, prompts_choices, prompt_call, token_usage, session_step)


def _autologging_enabled(
    experiment: "comet_ml.Experiment", kwargs: Dict[str, Any]
) -> bool:
    if not experiment.auto_metric_logging:
        return False

    if "stream" in kwargs and kwargs["stream"]:
        if not event_tracker.is_registered("openai_stream_warning", experiment.id):
            LOGGER.warning("OpenAI auto-logging is not supported when stream=True")
            event_tracker.register("openai_stream_warning", experiment.id)
        return False

    return True


def _log(
    experiment: "comet_ml.Experiment",
    prompts_choices: Iterator[Tuple[str, str]],
    prompt_call: Dict[str, Any],
    token_usage: Dict[str, int],
    step: int,
) -> None:
    log_to_experiment.token_metrics(experiment, token_usage, step)
    log_to_experiment.accumulated_prompt_calls(experiment, prompt_call)
    log_to_experiment.user_config(experiment)
    log_to_experiment.texts(experiment, prompts_choices, step)


def _processed_call_status(
    experiment: "comet_ml.Experiment", return_value: Any, step: int
) -> box.Box:
    is_error = monkey_patching.is_error_sentinel(return_value)
    log_to_experiment.call_status(experiment, is_error, step)

    if is_error:
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        log_to_experiment.token_metrics(experiment, usage, step)

    return box.Box(is_error=is_error)
