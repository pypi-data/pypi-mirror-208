# Copyright 2022-2023 The Wordcab Team. All rights reserved.
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

"""Wordcab API Utils functions."""

from typing import Any, Dict, List, Optional, Union

from .config import (
    CONTEXT_ELEMENTS,
    EXTRACT_PIPELINES,
    SOURCE_LANG,
    SUMMARY_LENGTHS_RANGE,
    SUMMARY_PIPELINES,
    TARGET_LANG,
    TRANSCRIPT_SPEAKER_MAPPING,
)
from .core_objects.utils import _get_deepgram_utterances


def format_deepgram_source(deepgram_json: Dict[str, Any]) -> List[str]:
    """
    Format the Deepgram json object to a list of strings.

    Parameters
    ----------
    deepgram_json : Dict[str, Any]
        The Deepgram json object.

    Returns
    -------
    List[str]
        The formatted list of strings.
    """
    utterances = _get_deepgram_utterances(deepgram_json)

    final_utterances: List[str] = []
    utt_to_add: str = ""

    for utt in utterances:
        if not utt_to_add:
            utt_to_add = f"SPEAKER {TRANSCRIPT_SPEAKER_MAPPING[int(utt['speaker'])]}: {utt['transcript']}"
        else:
            if utt["speaker"] == utterances[utterances.index(utt) - 1]["speaker"]:
                utt_to_add = f"{utt_to_add} {utt['transcript']}"
            else:
                final_utterances.append(utt_to_add)
                utt_to_add = f"SPEAKER {TRANSCRIPT_SPEAKER_MAPPING[int(utt['speaker'])]}: {utt['transcript']}"

    if utt_to_add:
        final_utterances.append(utt_to_add)

    return final_utterances


def _check_context_elements(elements: Optional[Union[str, List[str]]]) -> bool:
    """
    Check the context elements.

    Parameters
    ----------
    elements : Optional[Union[str, List[str]]]
        The context elements.

    Returns
    -------
    bool
        True if the context elements are valid, False otherwise.
    """
    if elements is None:
        return True

    if isinstance(elements, str):
        elements = [elements]

    for element in elements:
        if element not in CONTEXT_ELEMENTS:
            return False

    return True


def _check_source_lang(lang: str) -> bool:
    """
    Check the source language.

    Parameters
    ----------
    lang : str
        The source language.

    Returns
    -------
    bool
        True if the source language is valid, False otherwise.
    """
    if lang not in SOURCE_LANG:
        return False

    return True


def _check_target_lang(lang: str) -> bool:
    """
    Check the target language.

    Parameters
    ----------
    lang : str
        The target language.

    Returns
    -------
    bool
        True if the target language is valid, False otherwise.
    """
    if lang not in TARGET_LANG:
        return False

    return True


def _check_summary_length(lengths: Union[int, List[int]]) -> bool:
    """
    Check the summary lengths.

    Parameters
    ----------
    lengths : Union[int, List[int]]
        The summary lengths.

    Returns
    -------
    bool
        True if the summary lengths are valid, False otherwise.
    """
    if isinstance(lengths, int):
        lengths = [lengths]

    for length in lengths:
        if length < SUMMARY_LENGTHS_RANGE[0] or length > SUMMARY_LENGTHS_RANGE[1]:
            return False

    return True


def _check_summary_pipelines(pipelines: Union[str, List[str]]) -> bool:
    """
    Check the summary pipelines.

    Parameters
    ----------
    pipelines : Union[str, List[str]]
        The summary pipelines.

    Returns
    -------
    bool
        True if the summary pipelines are valid, False otherwise.
    """
    if isinstance(pipelines, str):
        pipelines = [pipelines]

    for pipeline in pipelines:
        if pipeline not in SUMMARY_PIPELINES:
            return False

    return True


def _check_extract_pipelines(pipelines: Union[str, List[str]]) -> bool:
    """
    Check the extract pipelines.

    Parameters
    ----------
    pipelines : Union[str, List[str]]
        The extract pipelines.

    Returns
    -------
    bool
        True if the extract pipelines are valid, False otherwise.
    """
    if isinstance(pipelines, str):
        pipelines = [pipelines]

    for pipeline in pipelines:
        if pipeline not in EXTRACT_PIPELINES:
            return False

    return True


def _format_context_elements(elements: Union[str, List[str]]) -> str:
    """
    Format the context.

    Parameters
    ----------
    elements : Union[str, List[str]]
        The context elements.

    Returns
    -------
    str
        The formatted context.
    """
    if isinstance(elements, str):
        return elements

    return ",".join(elements)


def _format_lengths(lengths: Union[int, List[int]]) -> str:
    """
    Format the lengths.

    Parameters
    ----------
    lengths : Union[int, List[int]]
        The lengths.

    Returns
    -------
    str
        The formatted lengths.
    """
    if isinstance(lengths, int):
        return str(lengths)

    return ",".join([str(length) for length in lengths])


def _format_pipelines(pipelines: Union[str, List[str]]) -> str:
    """
    Format the pipelines.

    Parameters
    ----------
    pipelines : Union[str, List[str]]
        The pipelines.

    Returns
    -------
    str
        The formatted pipelines.
    """
    if isinstance(pipelines, str):
        return pipelines

    return ",".join(pipelines)


def _format_tags(tags: Union[str, List[str]]) -> str:
    """
    Format the tags.

    Parameters
    ----------
    tags : Union[str, List[str]]
        The tags.

    Returns
    -------
    str
        The formatted tags.
    """
    if isinstance(tags, str):
        return tags

    return ",".join(tags)
