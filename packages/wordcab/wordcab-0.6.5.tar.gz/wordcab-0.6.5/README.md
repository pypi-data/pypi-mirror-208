<h1 align="center">Wordcab Python</h1>

<div align="center">
	<a  href="https://pypi.org/project/wordcab" target="_blank">
		<img src="https://img.shields.io/pypi/v/wordcab.svg" />
	</a>
	<a  href="https://pypi.org/project/wordcab" target="_blank">
		<img src="https://img.shields.io/pypi/pyversions/wordcab" />
	</a>
	<a  href="https://github.com/Wordcab/wordcab-python/blob/main/LICENSE" target="_blank">
		<img src="https://img.shields.io/pypi/l/wordcab" />
	</a>
	<a  href="https://github.com/Wordcab/wordcab-python/actions?workflow=Tests" target="_blank">
		<img src="https://github.com/Wordcab/wordcab-python/workflows/Tests/badge.svg" />
	</a>
	<a  href="https://app.codecov.io/gh/Wordcab/wordcab-python" target="_blank">
		<img src="https://codecov.io/gh/Wordcab/wordcab-python/branch/main/graph/badge.svg" />
	</a>
</div>
<br>
<div align="center">
	<a href="https://linkedin.com/company/wordcab" target="_blank">
		<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
	</a>
</div>

# What is Wordcab?

- **Summarize any business communications at scale with Wordcab's API.**
- **Wordcab** is a summarization service that provides a simple API to summarize any `audio`, `text`, or `JSON` file.
- It also includes compatibility with famous transcripts platforms like
  - [![AssemblyAI](https://img.shields.io/badge/AssemblyAI-blue)](https://www.assemblyai.com/)
  - [![Deepgram](https://img.shields.io/badge/Deepgram-green)](https://deepgram.com/)
  - [![Rev.ai](https://img.shields.io/badge/Rev.ai-orange)](https://www.rev.ai/)
  - [![Otter.ai](https://img.shields.io/badge/Otter.ai-purple)](https://otter.ai/)
  - [![Sonix.ai](https://img.shields.io/badge/Sonix.ai-yellow)](https://sonix.ai/)

# Getting started

You can learn more about Wordcab services and pricing on our [website](https://wordcab.com/).

If you want to try out the API, you can [signup](https://wordcab.com/signup/) for a free account and start using the API
right away.

# Requirements

- OS:
  - ![Linux](https://img.shields.io/badge/-Linux-orange?style=flat-square&logo=linux&logoColor=white)
  - ![Mac](https://img.shields.io/badge/-Mac-blue?style=flat-square&logo=apple&logoColor=white)
  - ![Windows](https://img.shields.io/badge/-Windows-blue?style=flat-square&logo=windows&logoColor=white)
- Python:
  - ![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)

# Installation

You can install _Wordcab Python_ via [pip] from [PyPI]:

```console
$ pip install wordcab
```

Start using the API with any python script right away!

# Usage

## Start Summary full pipeline

```python
import time
from wordcab import retrieve_job, retrieve_summary, start_summary
from wordcab.core_objects import AudioSource, GenericSource, InMemorySource


# Prepare your input source
## For a transcript stored as a .txt or .json file
source = GenericSource(filepath="path/to/file.txt")  # Or file.json
## For a transcript stored as an audio file
source = AudioSource(filepath="path/to/file.mp3")
## For a transcript already in memory
transcript = {"transcript": ["SPEAKER A: Hello.", "SPEAKER B: Hi."]}
source = InMemorySource(obj=transcript)

# Launch the Summarization job
job = start_summary(
	source_object=source,
	display_name="sample_txt",
	summary_type="narrative",
	summary_lens=[1, 3],
	tags=["sample", "text"],
)

# Wait for the job completion
while True:
	job = retrieve_job(job_name=job.job_name)
	if job.job_status == "SummaryComplete":
		break
	else:
		time.sleep(3)

# Get the summary id
summary_id = job.summary_details["summary_id"]
# Retrieve the summary
summary = retrieve_summary(summary_id=summary_id)

# Get the summary as a human-readable string
print(summary.get_formatted_summaries())

# Save the json object to a file
with open("wordcab_summary.json", "w") as f:
	f.write(summary)
```

# Documentation

Please see the [Documentation](https://wordcab-python.readthedocs.io/) for more details.

# Contributing

Contributions are very welcome. 🚀
To learn more, see the [Contributor Guide].

# License

- Distributed under the terms of the [![Apache 2.0 License Badge](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

- _Wordcab Python SDK_ is free and open source software.

# Issues

If you encounter any problems,
please [file an issue](https://github.com/Wordcab/wordcab-python/issues) along with a detailed description.

# Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/Wordcab/wordcab-python/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/Wordcab/wordcab-python/blob/main/LICENSE
[contributor guide]: https://github.com/Wordcab/wordcab-python/blob/main/CONTRIBUTING.md
[command-line reference]: https://wordcab-python.readthedocs.io/en/latest/usage.html
