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

"""Wordcab API Source object."""

import json
import logging
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union, no_type_check

import requests  # type: ignore
import validators  # type: ignore

from ..config import AVAILABLE_AUDIO_FORMATS, AVAILABLE_GENERIC_FORMATS, REQUEST_TIMEOUT
from .utils import (
    _get_assembly_utterances,
    _get_deepgram_utterances,
    _get_rev_monologues,
)


logger = logging.getLogger(__name__)


@dataclass
class BaseSource:
    """Base class for AudioSource and GenericSource objects. It is not meant to be used directly.

    Parameters
    ----------
    filepath : Optional[Union[str, Path]], optional
        Path to the local file, by default None.
    url : Optional[str], optional
        URL to the remote file, by default None.
    url_headers : Optional[Dict[str, str]], optional
        Headers to retrieve the file from the URL, by default None.
        Useful if the file requires authentication to be retrieved.

    Raises
    ------
    ValueError
        If neither `filepath` nor `url` are provided.
    ValueError
        If both `filepath` and `url` are provided.
    TypeError
        If `filepath` is not a string or a Path object.
    FileNotFoundError
        If `filepath` does not exist or is not accessible.

    Attributes
    ----------
    source : str
        The source type.
    source_type : str
        The source type.
    _stem : str
        The stem of the file.
    _suffix : str
        The suffix of the file.

    Returns
    -------
    BaseSource
        The source object.
    """

    filepath: Optional[Union[str, Path]] = field(default=None, repr=False)
    url: Optional[str] = field(default=None, repr=False)
    url_headers: Optional[Dict[str, str]] = field(default=None, repr=False)
    source: str = field(init=False)
    source_type: str = field(init=False)
    _stem: str = field(init=False, repr=False)
    _suffix: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        self.source = self.__class__.__name__
        if not self.filepath and not self.url:
            raise ValueError(
                "Please provide either a local or a remote source, respectively `filepath` or `url`."
            )
        if self.filepath and self.url:
            raise ValueError(
                "Please provide either a local or a remote source, not both `filepath` and `url`."
            )

        if self.filepath:
            if not isinstance(self.filepath, Path) and not isinstance(
                self.filepath, str
            ):
                raise TypeError(
                    f"The path must be a string or a Path object, not {type(self.filepath)}"
                )

            if isinstance(self.filepath, str):
                self.filepath = Path(self.filepath)

            if not self.filepath.exists():
                raise FileNotFoundError(
                    f"File {self.filepath} does not exist or is not accessible."
                )

            self._stem = self.filepath.stem
            self._suffix = self.filepath.suffix
            self.source_type = "local"

        if self.url:
            if self._check_if_url_is_valid():
                filename = urllib.parse.unquote(self.url.split("/")[-1])
                self._stem = ".".join(filename.split(".")[:-1])
                self._suffix = f".{filename.split('.')[-1].split('?')[0]}"
                self.source_type = "remote"

    @no_type_check
    def _load_file_from_path(self) -> bytes:
        """Load file from local path."""
        with open(self.filepath, "rb") as f:
            return f.read()

    def _load_file_from_url(self) -> requests.Response.content:
        """Load file from URL."""
        if self.url_headers:
            file = requests.get(
                self.url, headers=self.url_headers, timeout=REQUEST_TIMEOUT
            )
        else:
            file = requests.get(self.url, timeout=REQUEST_TIMEOUT)

        return file.content

    def _check_if_url_is_valid(self) -> bool:
        """Check if URL is valid."""
        if not validators.url(self.url):
            raise ValueError(f"Please provide a valid URL. {self.url} is not valid.")

        return True

    def prepare_payload(self) -> Union[str, bytes, Dict[str, bytes]]:
        """Prepare payload."""
        raise NotImplementedError("Payload preparation is not implemented yet.")

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers."""
        raise NotImplementedError("Headers preparation is not implemented yet.")


@dataclass
class InMemorySource:
    """In-memory source object.

    The in-memory source object is a special case of the generic source object.
    It is used to pass a pre-processed transcript to the API.

    Parameters
    ----------
    obj : Union[Dict[str, List[str]], List[str]]
        The in-memory object. It can be a list of strings or a dict with a `transcript` key
        and a list of strings as value.

    Raises
    ------
    ValueError
        If the in-memory object does not have a `transcript` key.
    TypeError
        If the in-memory object does not have a list as value for the `transcript` key.
    TypeError
        If the in-memory object is not a list or a dict.

    Examples
    --------
    >>> from wordcab.core_objects import InMemorySource

    >>> transcript = {"transcript": ["SPEAKER A: Hello.", "SPEAKER B: Hi."]}
    >>> in_memory_source = InMemorySource(obj=transcript)
    >>> in_memory_source
    InMemorySource(...)
    >>> in_memory_source.obj

    Returns
    -------
    InMemorySource
        The in-memory source object.
    """

    obj: Optional[Union[Dict[str, List[str]], List[str]]] = field(
        default=None, repr=False
    )
    source: str = field(init=False)
    source_type: str = field(init=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        self.source = "generic"
        self.source_type = "in_memory"
        if isinstance(self.obj, dict):
            if "transcript" not in self.obj:
                raise ValueError(
                    "Please provide a valid in-memory object. It must have a `transcript` key."
                )
            elif not isinstance(self.obj["transcript"], list):
                raise TypeError(
                    "Please provide a valid in-memory object. The `transcript` key must be a list."
                )
        elif isinstance(self.obj, list):
            self.obj = {"transcript": self.obj}
        else:
            raise TypeError(
                "Please provide a valid in-memory object. It must be a list or a dict."
            )

    def prepare_payload(self) -> str:
        """Prepare payload for API request."""
        self.payload = json.dumps(self.obj)
        return self.payload

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        return self.headers


@dataclass
class GenericSource(BaseSource):
    """Generic source object.

    The GenericSource object is required to create a job that uses a generic file as input,
    such as `.txt` or `.json` file.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the local file.
    url : str
        The URL to the remote file.

    Raises
    ------
    ValueError
        If the file format is not supported.
    ValueError
        If both `filepath` and `url` are provided.
    TypeError
        If the path is not a string or a Path object.
    FileNotFoundError
        If the file does not exist or is not accessible.

    Examples
    --------
    >>> from wordcab.core_objects import GenericSource

    >>> generic_source = GenericSource(filepath="path/to/generic/file.txt")  # doctest: +SKIP
    >>> generic_source  # doctest: +SKIP
    GenericSource(...)
    >>> generic_source.file_object  # doctest: +SKIP
    b'Hello, world!'
    >>> generic_source.source_type  # doctest: +SKIP
    'local'
    >>> generic_source._suffix  # doctest: +SKIP
    '.txt'
    >>> generic_source._stem  # doctest: +SKIP
    'file'

    Returns
    -------
    GenericSource
        The generic source object.
    """

    file_object: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.source = "generic"

        if self._suffix not in AVAILABLE_GENERIC_FORMATS:
            raise ValueError(
                f"Please provide a valid file format. {self._suffix} is not valid."
            )
        if self.source_type == "local":
            self.file_object = self._load_file_from_path()
        elif self.source_type == "remote":
            self.file_object = self._load_file_from_url()

    def prepare_payload(self) -> str:
        """Prepare payload for API request."""
        if self._suffix == ".json":
            self.payload = json.dumps({"transcript": json.loads(self.file_object)})
        elif self._suffix == ".txt":
            self.payload = json.dumps(
                {"transcript": self.file_object.decode("utf-8").splitlines()}
            )
        return self.payload

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        return self.headers


@dataclass
class AudioSource(BaseSource):
    """
    The AudioSource object is required to create a job that uses an audio file as input.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the local file.
    url : str
        The URL to the remote file.

    Raises
    ------
    ValueError
        If the file format is not supported.
    ValueError
        If both `filepath` and `url` are provided.
    TypeError
        If the path is not a string or a Path object.
    FileNotFoundError
        If the file does not exist or is not accessible.

    Examples
    --------
    >>> from wordcab.core_objects import AudioSource

    >>> audio_source = AudioSource(filepath="path/to/audio/file.mp3")  # doctest: +SKIP
    >>> audio_source  # doctest: +SKIP
    AudioSource(...)

    Returns
    -------
    AudioSource
        The audio source object.
    """

    file_object: bytes = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.source = "audio"
        if self._suffix not in AVAILABLE_AUDIO_FORMATS:
            raise ValueError(
                f"Please provide a valid file format. {self._suffix} is not valid."
            )
        if self.source_type == "local":
            self.file_object = self._load_file_from_path()
        elif self.source_type == "remote":
            self.file_object = self._load_file_from_url()

    def prepare_payload(self) -> Dict[str, bytes]:
        """Prepare payload for API request."""
        self.payload = {"audio_file": self.file_object}
        return self.payload

    @no_type_check
    def prepare_headers(self) -> dict:
        """Prepare headers for API request."""
        self.headers = {}
        return self.headers


@dataclass
class WordcabTranscriptSource:
    """
    Wordcab transcript source object using a Wordcab transcript ID.

    Parameters
    ----------
    transcript_id : str
        The Wordcab transcript ID to use as input.

    Raises
    ------
    ValueError
        If the `transcript_id` is not provided.

    Examples
    --------
    >>> from wordcab.core_objects import WordcabTranscriptSource

    >>> wordcab_transcript_source = WordcabTranscriptSource(transcript_id="transcript_12345")
    >>> wordcab_transcript_source
    WordcabTranscriptSource(transcript_id=transcript_12345)

    Returns
    -------
    WordcabTranscriptSource
        The Wordcab transcript source object.
    """

    transcript_id: Optional[str] = field(default=None)
    source: str = field(init=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        if self.transcript_id is None:
            raise ValueError(
                "Please provide a `transcript_id` to initialize a WordcabTranscriptSource object."
            )
        self.source = "wordcab_transcript"

    def __repr__(self) -> str:
        """Representation method."""
        return f"WordcabTranscriptSource(transcript_id={self.transcript_id})"

    def prepare_payload(self) -> None:
        """Prepare payload for API request."""
        return None

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {"Accept": "application/json"}
        return self.headers


@dataclass
class SignedURLSource(BaseSource):
    """Signed URL source object."""

    signed_url: Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.signed_url = self.url
        self.source = "signed_url"
        raise NotImplementedError("Signed URL source is not implemented yet.")


@dataclass
class AssemblyAISource(BaseSource):
    """
    AssemblyAI source object using a local or remote AssemblyAI JSON file.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the local file.
    url : str
        The URL to the remote file.

    Raises
    ------
    ValueError
        If the file format is not valid.

    Examples
    --------
    >>> from wordcab.core_objects import AssemblyAISource

    >>> assemblyai_source = AssemblyAISource(filepath="path/to/assemblyai/file.json")  # doctest: +SKIP
    >>> assemblyai_source  # doctest: +SKIP
    AssemblyAISource(...)
    >>> assemblyai_source.source  # doctest: +SKIP
    'assembly_ai'

    Returns
    -------
    AssemblyAISource
        The AssemblyAI source object.
    """

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.source = "assembly_ai"

        if self._suffix != ".json":
            raise ValueError(
                f"Please provide a valid AssemblyAI file format. {self._suffix} is not valid, it should be .json."
            )

        if self.source_type == "local":
            self.file_object = self._load_file_from_path()
        elif self.source_type == "remote":
            self.file_object = self._load_file_from_url()

    def prepare_payload(self) -> str:
        """Prepare payload for API request."""
        self.payload = json.dumps(
            _get_assembly_utterances(json.loads(self.file_object))
        )
        return self.payload

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        return self.headers


@dataclass
class DeepgramSource(BaseSource):
    """
    Deepgram source object using a local or remote Deepgram JSON file.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the local file.
    url : str
        The URL to the remote file.

    Raises
    ------
    ValueError
        If the file format is not valid.

    Examples
    --------
    >>> from wordcab.core_objects import DeepgramSource

    >>> deepgram_source = DeepgramSource(filepath="path/to/deepgram/file.json")  # doctest: +SKIP
    >>> deepgram_source  # doctest: +SKIP
    DeepgramSource(...)
    >>> deepgram_source.source  # doctest: +SKIP
    'deepgram'

    Returns
    -------
    DeepgramSource
        The Deepgram source object.
    """

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.source = "deepgram"

        if self._suffix != ".json":
            raise ValueError(
                f"Please provide a valid Deepgram file format. {self._suffix} is not valid, it should be .json."
            )

        if self.source_type == "local":
            self.file_object = self._load_file_from_path()
        elif self.source_type == "remote":
            self.file_object = self._load_file_from_url()

    def prepare_payload(self) -> str:
        """Prepare payload for API request."""
        self.payload = json.dumps(
            _get_deepgram_utterances(json.loads(self.file_object))
        )
        return self.payload

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        return self.headers


@dataclass
class RevSource(BaseSource):
    """
    Rev.ai source object using a local or remote Rev.ai JSON file.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the local file.
    url : str
        The URL to the remote file.

    Raises
    ------
    ValueError
        If the file format is not valid.

    Examples
    --------
    >>> from wordcab.core_objects import RevSource

    >>> rev_source = RevSource(filepath="path/to/rev/file.json")  # doctest: +SKIP
    >>> rev_source  # doctest: +SKIP
    RevSource(...)
    >>> rev_source.source  # doctest: +SKIP
    'rev_ai'

    Returns
    -------
    RevSource
        The Rev.ai source object.
    """

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.source = "rev_ai"

        if self._suffix != ".json":
            raise ValueError(
                f"Please provide a valid Rev.ai file format. {self._suffix} is not valid, it should be .json."
            )

        if self.source_type == "local":
            self.file_object = self._load_file_from_path()
        elif self.source_type == "remote":
            self.file_object = self._load_file_from_url()

    def prepare_payload(self) -> str:
        """Prepare payload for API request."""
        self.payload = json.dumps(_get_rev_monologues(json.loads(self.file_object)))
        return self.payload

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        return self.headers


@dataclass
class VTTSource(BaseSource):
    """
    VTT source object using a local or remote VTT file.

    Parameters
    ----------
    filepath : Union[str, Path]
        The path to the local file.
    url : str
        The URL to the remote file.

    Raises
    ------
    ValueError
        If the file format is not valid.

    Examples
    --------
    >>> from wordcab.core_objects import VTTSource

    >>> vtt_source = VTTSource(filepath="path/to/vtt/file.vtt")  # doctest: +SKIP
    >>> vtt_source  # doctest: +SKIP
    VTTSource(...)
    >>> vtt_source.source  # doctest: +SKIP
    'vtt'

    Returns
    -------
    VTTSource
        The VTT source object.
    """

    filename: str = field(init=False)

    def __post_init__(self) -> None:
        """Post-init method."""
        super().__post_init__()
        self.source = "vtt"

        if self._suffix != ".vtt":
            raise ValueError(
                f"Please provide a valid VTT file format. {self._suffix} is not valid, it should be .vtt."
            )

        if self.source_type == "local":
            self.file_object = self._load_file_from_path()
        elif self.source_type == "remote":
            self.file_object = self._load_file_from_url()

        self.filename = self.filepath.name  # type: ignore

    def prepare_payload(self) -> bytes:
        """Prepare payload for API request."""
        self.payload: bytes = self.file_object
        return self.payload

    def prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API request."""
        self.headers = {
            "Content-Disposition": f"attachment; filename={self.filename}",
        }
        return self.headers
