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

"""Wordcab API Summary object."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from ..config import SUMMARY_TYPES
from .utils import _get_context_items, _textwrap


logger = logging.getLogger(__name__)


@dataclass
class StructuredSummary:
    """Structured summary object."""

    summary: Union[str, Dict[str, str]]
    context: Optional[
        Dict[str, Union[str, List[str], Dict[str, Union[str, List[str]]]]]
    ] = field(default=None)
    summary_html: Optional[Union[str, Dict[str, str]]] = field(default=None)
    end: Optional[str] = field(default=None)
    end_index: Optional[int] = field(default=None)
    start: Optional[str] = field(default=None)
    start_index: Optional[int] = field(default=None)
    timestamp_end: Optional[int] = field(default=None)
    timestamp_start: Optional[int] = field(default=None)
    transcript_segment: Optional[List[Dict[str, Union[str, int]]]] = field(default=None)

    def __repr__(self) -> str:
        """Return a string representation of the object without the None values."""
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items() if v is not None)})"


@dataclass
class BaseSummary:
    """Summary object."""

    job_status: str
    summary_id: str
    display_name: Optional[str] = field(default=None)
    job_name: Optional[str] = field(default=None)
    process_time: Optional[str] = field(default=None)
    speaker_map: Optional[Dict[str, str]] = field(default=None)
    source: Optional[str] = field(default=None)
    source_lang: Optional[str] = field(default=None)
    summary_type: Optional[str] = field(default=None)
    summary: Optional[Dict[str, Any]] = field(default=None)
    target_lang: Optional[str] = field(default=None)
    transcript_id: Optional[str] = field(default=None)
    time_started: Optional[str] = field(default=None)
    time_completed: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        """Post init."""
        if self.summary_type:
            if self.summary_type not in SUMMARY_TYPES:
                raise ValueError(
                    f"Summary type must be one of {SUMMARY_TYPES}, not {self.summary_type}"
                )

        if self.time_started and self.time_completed:
            if self.time_started == self.time_completed:
                raise ValueError("time_started and time_completed must be different")

    def get_summaries(self) -> Dict[str, List[Union[str, List[str]]]]:
        """
        Get the summaries as a dictionary with the summary length as key and the summaries as values.

        Returns
        -------
        Dict[str, List[Union[str, List[str]]]]
            The summaries as a dictionnary with the summary length as key and the summaries as values.
            If the summary type is brief, the summaries are returned as a list of list of str,
            otherwise they are returned as a list of str.
        """
        if self.summary is None:
            return {}

        summaries: Dict[str, Any] = {}

        for summary_len in self.summary:
            summaries_list = [
                s.summary for s in self.summary[summary_len]["structured_summary"]
            ]

            if self.summary_type == "brief":
                summaries_list = [
                    [s["title"], s["brief_summary"]] for s in summaries_list
                ]

            summaries[summary_len] = summaries_list

        return summaries

    def get_formatted_summaries(
        self, add_context: Optional[bool] = False
    ) -> Dict[str, str]:
        """Format the summaries in an human readable format.

        Return the summaries as a dictionary in an human readable format with the summary length as key
        and the summaries as values.

        Parameters
        ----------
        add_context : bool, optional
            If True, add the context items to the summary, by default False.

        Returns
        -------
        Dict[str, str]
            The summaries as a dictionary with the summary length as key and the summaries as values formatted
            in an human readable format.
        """
        if self.summary is None:
            return {}

        summaries: Dict[str, Any] = {}

        if self.summary is None:
            raise ValueError("No summary available.")

        if self.summary_type is None:
            raise ValueError("No summary type found.")

        for summary_len in self.summary:
            summaries[summary_len] = _format_summary(
                self.summary[summary_len]["structured_summary"],
                self.summary_type,
                summary_len,
                add_context,
            )

        return summaries


@dataclass
class ListSummaries:
    """List summaries object."""

    page_count: int
    next_page: str
    results: List[BaseSummary]


def _format_summary(
    structured_summaries: List[StructuredSummary],
    summary_type: str,
    summary_len: str,
    add_context: Optional[bool] = False,
) -> str:
    """
    Format the summary in an human readable format.

    Parameters
    ----------
    structured_summaries : list
        The structured summaries list.
    summary_type : str
        The summary type.
    summary_len : str
        The summary length.
    add_context : bool, optional
        If True, add the context items to the summary. By default False.

    Returns
    -------
    str
        The summary formatted in an human readable format.
    """
    total_summary = len(structured_summaries)

    txt = f"{summary_type} - length: {summary_len}\n\n"
    for i in range(total_summary):
        txt += f"[{i + 1}/{total_summary}]\n"

        summary = structured_summaries[i].summary

        if isinstance(summary, dict):
            txt += f"Title: {summary['title']}\nSummary: {summary['brief_summary']}\n\n"

        if isinstance(summary, str):
            txt += f"{_textwrap(summary)}\n\n"

        if add_context:
            context_items = structured_summaries[i].context

            if context_items is not None:
                txt += f"{_get_context_items(context_items)}\n\n"

    return txt
