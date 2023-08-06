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

"""Wordcab API Client."""

import logging
from typing import Dict, List, Optional, Union, no_type_check

import requests  # type: ignore

from .config import (
    CONTEXT_ELEMENTS,
    EXTRACT_PIPELINES,
    LIST_JOBS_ORDER_BY,
    REQUEST_TIMEOUT,
    SOURCE_LANG,
    SOURCE_OBJECT_MAPPING,
    SUMMARY_LENGTHS_RANGE,
    SUMMARY_PIPELINES,
    SUMMARY_TYPES,
    TARGET_LANG,
)
from .core_objects import (
    BaseSource,
    BaseSummary,
    BaseTranscript,
    ExtractJob,
    InMemorySource,
    JobSettings,
    ListJobs,
    ListSummaries,
    ListTranscripts,
    Stats,
    StructuredSummary,
    SummarizeJob,
    TranscriptUtterance,
    WordcabTranscriptSource,
)
from .login import get_token
from .utils import (
    _check_context_elements,
    _check_extract_pipelines,
    _check_source_lang,
    _check_summary_length,
    _check_summary_pipelines,
    _check_target_lang,
    _format_context_elements,
    _format_lengths,
    _format_pipelines,
    _format_tags,
)


logger = logging.getLogger(__name__)


class Client:
    """Wordcab API Client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client."""
        self.api_key = api_key if api_key else get_token()
        if not self.api_key:
            raise ValueError(
                """
            API Key not found. You must set the WORDCAB_API_KEY environment variable. Use `wordcab login` to login
            to the Wordcab CLI and set the environment variable.
            """
            )
        self.timeout = REQUEST_TIMEOUT

    def __enter__(self) -> "Client":
        """Enter the client context."""
        return self

    def __exit__(
        self,
        exception_type: Optional[Union[ValueError, TypeError, AssertionError]],
        exception_value: Optional[Exception],
        traceback: Optional[Exception],
    ) -> None:
        """Exit the client context."""
        pass

    @no_type_check
    def request(
        self,
        method: str,
        **kwargs: Union[bool, int, str, Dict[str, str], List[int], List[str]],
    ) -> Union[
        BaseSource,
        BaseSummary,
        BaseTranscript,
        ExtractJob,
        ListJobs,
        ListSummaries,
        ListTranscripts,
        Stats,
        SummarizeJob,
        Union[ExtractJob, SummarizeJob],
    ]:
        """Make a request to the Wordcab API."""
        if not method:
            raise ValueError("You must specify a method.")
        return getattr(self, method)(**kwargs)

    def get_stats(
        self,
        min_created: Optional[str] = None,
        max_created: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Stats:
        """Get the stats of the account."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        params: Dict[str, str] = {}
        if min_created:
            params["min_created"] = min_created
        if max_created:
            params["max_created"] = max_created
        if tags:
            params["tags"] = _format_tags(tags)

        r = requests.get(
            "https://wordcab.com/api/v1/me",
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            return Stats(**r.json())
        else:
            raise ValueError(r.text)

    def start_extract(  # noqa: C901
        self,
        source_object: Union[BaseSource, InMemorySource, WordcabTranscriptSource],
        display_name: str,
        ephemeral_data: Optional[bool] = False,
        only_api: Optional[bool] = True,
        pipelines: Union[str, List[str]] = [  # noqa: B006
            "questions_answers",
            "topic_segments",
            "emotions",
            "speaker_talk_ratios",
        ],
        split_long_utterances: Optional[bool] = False,
        tags: Optional[Union[str, List[str]]] = None,
    ) -> ExtractJob:
        """Start an Extraction job."""
        if _check_extract_pipelines(pipelines) is False:
            raise ValueError(
                f"""
                You must specify a valid list of pipelines.
                Available pipelines are: {", ".join(EXTRACT_PIPELINES[:-1])} and {EXTRACT_PIPELINES[-1]}.
            """
            )
        if (
            isinstance(
                source_object, (BaseSource, InMemorySource, WordcabTranscriptSource)
            )
            is False
        ):
            raise ValueError(
                """
                You must specify a valid source object for the extraction job.
                See https://docs.wordcab.com/docs/accepted-sources for more information.
            """
            )

        source = source_object.source
        if source not in SOURCE_OBJECT_MAPPING.keys():
            raise ValueError(
                f"Invalid source: {source}. Source must be one of {SOURCE_OBJECT_MAPPING.keys()}"
            )
        if (
            source_object.__class__.__name__ != SOURCE_OBJECT_MAPPING[source]
            and source_object.__class__.__name__ != "InMemorySource"
        ):
            raise ValueError(
                f"""
                Invalid source object: {source_object}. Source object must be of type {SOURCE_OBJECT_MAPPING[source]},
                but is of type {type(source_object)}.
            """
            )

        if hasattr(source_object, "payload"):
            payload = source_object.payload
        else:
            payload = source_object.prepare_payload()

        if hasattr(source_object, "headers"):
            headers = source_object.headers
        else:
            headers = source_object.prepare_headers()
        headers["Authorization"] = f"Bearer {self.api_key}"

        pipelines = _format_pipelines(pipelines)
        params: Dict[str, Union[str, None]] = {
            "source": source,
            "display_name": display_name,
            "ephemeral_data": str(ephemeral_data).lower(),
            "only_api": str(only_api).lower(),
            "pipeline": pipelines,
            "split_long_utterances": str(split_long_utterances).lower(),
        }
        if tags:
            params["tags"] = _format_tags(tags)

        if source == "wordcab_transcript" and hasattr(source_object, "transcript_id"):
            params["transcript_id"] = source_object.transcript_id
        if source == "signed_url" and hasattr(source_object, "signed_url"):
            params["signed_url"] = source_object.signed_url

        if source == "audio" or source == "vtt":
            r = requests.post(
                "https://wordcab.com/api/v1/extract",
                headers=headers,
                params=params,
                files=payload,
                timeout=self.timeout,
            )
        else:
            r = requests.post(
                "https://wordcab.com/api/v1/extract",
                headers=headers,
                params=params,
                data=payload,
                timeout=self.timeout,
            )

        if r.status_code == 201:
            logger.info("Extract job started.")
            return ExtractJob(
                display_name=display_name,
                job_name=r.json()["job_name"],
                source=source,
                settings=JobSettings(
                    ephemeral_data=ephemeral_data,
                    only_api=only_api,
                    pipeline=pipelines,
                    split_long_utterances=split_long_utterances,
                ),
            )
        else:
            raise ValueError(r.text)

    def start_summary(  # noqa: C901
        self,
        source_object: Union[BaseSource, InMemorySource, WordcabTranscriptSource],
        display_name: str,
        summary_type: str,
        context: Optional[Union[str, List[str]]] = None,
        ephemeral_data: Optional[bool] = False,
        only_api: Optional[bool] = True,
        pipelines: Union[str, List[str]] = ["transcribe", "summarize"],  # noqa: B006
        source_lang: Optional[str] = None,
        split_long_utterances: Optional[bool] = False,
        summary_lens: Optional[Union[int, List[int]]] = None,
        target_lang: Optional[str] = None,
        tags: Optional[Union[str, List[str]]] = None,
    ) -> SummarizeJob:
        """Start a Summary job."""
        if summary_type not in SUMMARY_TYPES:
            raise ValueError(
                f"Invalid summary type. Available types are: {', '.join(SUMMARY_TYPES)}"
            )

        if summary_type == "reason_conclusion":
            raise ValueError(
                """
                The summary type 'reason_conclusion' has been removed. You can use `brief` instead.
            """
            )
        else:
            if summary_lens is None:
                logger.warning(
                    "You have not specified a summary length. Defaulting to 3."
                )
                summary_lens = 3
            if _check_summary_length(summary_lens) is False:
                raise ValueError(
                    f"""
                    You must specify a valid summary length. Summary length must be an integer or a list of integers.
                    The integer values must be between {SUMMARY_LENGTHS_RANGE[0]} and {SUMMARY_LENGTHS_RANGE[1]}.
                """
                )

        if _check_summary_pipelines(pipelines) is False:
            raise ValueError(
                f"""
                You must specify a valid list of pipelines.
                Available pipelines are: {", ".join(SUMMARY_PIPELINES[:-1])} and {SUMMARY_PIPELINES[-1]}.
            """
            )

        if (
            isinstance(
                source_object, (BaseSource, InMemorySource, WordcabTranscriptSource)
            )
            is False
        ):
            raise ValueError(
                """
                You must specify a valid source object to summarize.
                See https://docs.wordcab.com/docs/accepted-sources for more information.
            """
            )

        if _check_context_elements(context) is False:
            raise ValueError(
                f"""
                You must specify valid context elements. Context elements must be a string or a list of strings.
                Here are the available context elements: {", ".join(CONTEXT_ELEMENTS[:-1])} and {CONTEXT_ELEMENTS[-1]}.
            """
            )

        if source_lang is None:
            source_lang = "en"

        if target_lang is None:
            target_lang = source_lang

        if _check_source_lang(source_lang) is False:
            raise ValueError(
                f"""
                You must specify a valid source language.
                Available languages are: {", ".join(SOURCE_LANG[:-1])} or {SOURCE_LANG[-1]}.
            """
            )
        elif _check_target_lang(target_lang) is False:
            raise ValueError(
                f"""
                You must specify a valid target language.
                Available languages are: {", ".join(TARGET_LANG[:-1])} or {TARGET_LANG[-1]}.
            """
            )
        elif source_lang != "en" or target_lang != "en":
            logger.warning(
                """
                Languages outside `en` are currently in beta and may not be as accurate as the English model.
                We are working to improve the accuracy of the non-English models.
                If you have any feedback, don't hesitate to get in touch with us at info@wordcab.com.
            """
            )

        source = source_object.source
        if source not in SOURCE_OBJECT_MAPPING.keys():
            raise ValueError(
                f"Invalid source: {source}. Source must be one of {SOURCE_OBJECT_MAPPING.keys()}"
            )
        if (
            source_object.__class__.__name__ != SOURCE_OBJECT_MAPPING[source]
            and source_object.__class__.__name__ != "InMemorySource"
        ):
            raise ValueError(
                f"""
                Invalid source object: {source_object}. Source object must be of type {SOURCE_OBJECT_MAPPING[source]},
                but is of type {type(source_object)}.
            """
            )

        if hasattr(source_object, "payload"):
            payload = source_object.payload
        else:
            payload = source_object.prepare_payload()

        if hasattr(source_object, "headers"):
            headers = source_object.headers
        else:
            headers = source_object.prepare_headers()
        headers["Authorization"] = f"Bearer {self.api_key}"

        pipelines = _format_pipelines(pipelines)
        params: Dict[str, Union[str, None]] = {
            "source": source,
            "display_name": display_name,
            "ephemeral_data": str(ephemeral_data).lower(),
            "only_api": str(only_api).lower(),
            "pipeline": pipelines,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "split_long_utterances": str(split_long_utterances).lower(),
            "summary_type": summary_type,
        }
        if context:
            params["context"] = _format_context_elements(context)
        if summary_lens:
            params["summary_lens"] = _format_lengths(summary_lens)
        if tags:
            params["tags"] = _format_tags(tags)

        if source == "wordcab_transcript" and hasattr(source_object, "transcript_id"):
            params["transcript_id"] = source_object.transcript_id
        if source == "signed_url" and hasattr(source_object, "signed_url"):
            params["signed_url"] = source_object.signed_url

        if source == "audio":
            r = requests.post(
                "https://wordcab.com/api/v1/summarize",
                headers=headers,
                params=params,
                files=payload,
                timeout=self.timeout,
            )
        else:
            r = requests.post(
                "https://wordcab.com/api/v1/summarize",
                headers=headers,
                params=params,
                data=payload,
                timeout=self.timeout,
            )

        if r.status_code == 201:
            logger.info("Summary job started.")
            return SummarizeJob(
                display_name=display_name,
                job_name=r.json()["job_name"],
                source=source,
                settings=JobSettings(
                    ephemeral_data=ephemeral_data,
                    pipeline=pipelines,
                    split_long_utterances=split_long_utterances,
                    only_api=only_api,
                ),
            )
        else:
            raise ValueError(r.text)

    def list_jobs(
        self,
        page_size: Optional[int] = 100,
        page_number: Optional[int] = None,
        order_by: Optional[str] = "-time_started",
    ) -> ListJobs:
        """List all jobs."""
        if order_by not in LIST_JOBS_ORDER_BY:
            raise ValueError(
                f"""
                Invalid `order_by` parameter. Must be one of {LIST_JOBS_ORDER_BY}.
                You can use - to indicate descending order.
            """
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        params = {"page_size": page_size, "order_by": order_by}

        if page_number is not None:
            params["page"] = page_number

        r = requests.get(
            "https://wordcab.com/api/v1/jobs",
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            data = r.json()
            list_jobs: List[Union[ExtractJob, SummarizeJob]] = []
            for job in data["results"]:
                if "summary_details" in job:
                    list_jobs.append(SummarizeJob(**job))
                else:
                    list_jobs.append(ExtractJob(**job))
            return ListJobs(
                page_count=int(data["page_count"]),
                next_page=data.get("next"),
                results=list_jobs,
            )
        else:
            raise ValueError(r.text)

    def retrieve_job(self, job_name: str) -> Union[ExtractJob, SummarizeJob]:
        """Retrieve a job."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        r = requests.get(
            f"https://wordcab.com/api/v1/jobs/{job_name}",
            headers=headers,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            data = r.json()
            if "summary_details" in data:
                return SummarizeJob(**data)
            else:
                return ExtractJob(**data)
        else:
            raise ValueError(r.text)

    @no_type_check
    def delete_job(self, job_name: str, warning: bool = True) -> Dict[str, str]:
        """Delete a job."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        r = requests.delete(
            f"https://wordcab.com/api/v1/jobs/{job_name}",
            headers=headers,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            if warning:
                logger.warning(f"Job {job_name} deleted.")
            return r.json()
        else:
            raise ValueError(r.text)

    def list_transcripts(
        self, page_size: Optional[int] = 100, page_number: Optional[int] = None
    ) -> ListTranscripts:
        """List all transcripts."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        params = {"page_size": page_size}

        if page_number is not None:
            params["page"] = page_number

        r = requests.get(
            "https://wordcab.com/api/v1/transcripts",
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            data = r.json()
            return ListTranscripts(
                page_count=int(data["page_count"]),
                next_page=data.get("next"),
                results=[
                    BaseTranscript(**transcript) for transcript in data["results"]
                ],
            )
        else:
            raise ValueError(r.text)

    def retrieve_transcript(self, transcript_id: str) -> BaseTranscript:
        """Retrieve a transcript."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        r = requests.get(
            f"https://wordcab.com/api/v1/transcripts/{transcript_id}",
            headers=headers,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            data = r.json()
            utterances = data.pop("transcript")
            transcript = BaseTranscript(**data)
            for utterance in utterances:
                transcript.transcript.append(TranscriptUtterance(**utterance))
            return transcript
        else:
            raise ValueError(r.text)

    def change_speaker_labels(
        self, transcript_id: str, speaker_map: Dict[str, str]
    ) -> BaseTranscript:
        """Change the speaker labels of a transcript."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        r = requests.patch(
            f"https://wordcab.com/api/v1/transcripts/{transcript_id}",
            headers=headers,
            json={"speaker_map": speaker_map},
            timeout=self.timeout,
        )

        if r.status_code == 200:
            logger.info("Speaker labels changed.")
            return BaseTranscript(**r.json())
        else:
            raise ValueError(r.text)

    def list_summaries(
        self, page_size: Optional[int] = 100, page_number: Optional[int] = None
    ) -> ListSummaries:
        """List all summaries."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        params = {"page_size": page_size}

        if page_number is not None:
            params["page"] = page_number

        r = requests.get(
            "https://wordcab.com/api/v1/summaries",
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            data = r.json()
            return ListSummaries(
                page_count=int(data["page_count"]),
                next_page=data.get("next"),
                results=[BaseSummary(**summary) for summary in data["results"]],
            )
        else:
            raise ValueError(r.text)

    def retrieve_summary(self, summary_id: str) -> BaseSummary:
        """Retrieve a summary."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        r = requests.get(
            f"https://wordcab.com/api/v1/summaries/{summary_id}",
            headers=headers,
            timeout=self.timeout,
        )

        if r.status_code == 200:
            data = r.json()
            structured_summaries = data.pop("summary")
            summary = BaseSummary(**data)
            summaries: Dict[
                str,
                Dict[str, List[StructuredSummary]],
            ] = {}
            for key, value in structured_summaries.items():
                summaries[key] = {
                    "structured_summary": [
                        StructuredSummary(**items)
                        for items in value["structured_summary"]
                    ]
                }
            summary.summary = summaries
            return summary
        else:
            raise ValueError(r.text)
