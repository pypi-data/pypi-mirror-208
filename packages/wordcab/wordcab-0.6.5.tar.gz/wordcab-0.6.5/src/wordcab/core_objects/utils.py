# Copyright 2023 The Wordcab Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Wordcab core objects utils functions."""

import textwrap
from typing import Any, Dict


def _get_context_items(
    context: Dict[str, Any],
) -> str:
    """Get the context items."""
    context_items = ""

    if "issue" in context:
        context_items += f"Issue: {context['issue']}\n"

    if "purpose" in context:
        context_items += f"Purpose: {context['purpose']}\n"

    if "next_steps" in context:
        context_items += f"Next steps: {context['next_steps']}\n"

    if "discussion_points" in context:
        context_items += f"Discussion points: {context['discussion_points']}\n"

    if "keywords" in context:
        context_items += f"Keywords: {context['keywords']}\n"

    return context_items


def _get_assembly_utterances(assembly_json: Dict[str, Any]) -> Any:
    """Get the AssemblyAI utterances."""
    utterances = assembly_json.pop("utterances", None)

    if utterances is None:
        raise ValueError(
            "No utterances key found. Verify the AssemblyAI json file you are using."
        )

    return utterances


def _get_deepgram_utterances(deepgram_json: Dict[str, Any]) -> Any:
    """Get the Deepgram utterances."""
    results = deepgram_json.pop("results", None)

    if results is None:
        raise ValueError(
            "No results key found. Verify the Deepgram json file you are using."
        )

    utterances = results.pop("utterances", None)

    if utterances is None:
        raise ValueError(
            "No utterances key found. Verify the Deepgram json file you are using."
        )

    return utterances


def _get_rev_monologues(rev_json: Dict[str, Any]) -> Any:
    """Get the Rev.ai monologues."""
    monologues = rev_json.pop("monologues", None)

    if monologues is None:
        raise ValueError(
            "No monologues key found. Verify the Rev.ai json file you are using."
        )

    return monologues


def _textwrap(text_to_wrap: str, width: int = 80) -> str:
    """
    Return a formatted string with the text wrapped to the specified width using textwrap.

    Parameters
    ----------
    text_to_wrap : str
        The text to wrap.
    width : int
        The width to wrap the text to, by default 80.

    Returns
    -------
    str
        The formatted string with the text wrapped to the specified width.
    """
    return "\n".join(textwrap.wrap(text_to_wrap, width=width))
