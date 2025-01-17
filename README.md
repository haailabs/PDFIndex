# PDF Paper Index

A Python tool that automatically extracts metadata from academic papers in PDF format using the Groq LLM API. This tool processes PDFs to extract key bibliographic information including titles, authors, abstracts, and more.

## Features

- Extracts metadata from academic papers in PDF format including:
  - Title
  - Authors
  - Year
  - Journal/Conference name
  - DOI
  - Keywords
  - Abstract
- Processes multiple PDFs in a directory
- Saves results in JSON format
- Includes retry mechanisms for API calls
- Handles partial or unreadable PDFs gracefully

## Prerequisites

- Python 3.6+
- Groq API key

## Installation

1. Clone this repository or download the source code
2. Install required dependencies:

```bash
pip install openai pypdf2
```

3. Set up your Groq API key as an environment variable:

```bash
export GROQ_API_KEY="your-api-key-here"
```

## Usage

1. Run the script:

```bash
python extract_metadata.py
```

2. When prompted, enter the directory path containing your PDF papers.

The script will:
- Process each PDF in the directory
- Extract metadata using the Groq LLM API
- Print results to the console
- Save all metadata to `metadata.json`

## Output Format

The tool generates a JSON file with the following structure for each paper:

```json
{
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "year": "2024",
  "journal": "Journal Name",
  "doi": "10.xxxx/xxxxx",
  "keywords": ["keyword1", "keyword2"],
  "abstract": "Paper abstract text...",
  "filename": "paper.pdf"
}
```

## Error Handling

- If a field cannot be extracted, it will be marked as "unknown"
- Failed API calls are retried up to 3 times with exponential backoff
- Partial PDF processing is supported - if some pages fail to process, the tool continues with available text
- Processes the first 3 pages of each PDF, sometimes metadata are not just on the first page
- Requires clear text extraction from PDFs (scanned PDFs may not work well)

## Contributing

Feel free to submit issues and pull requests for improvements.

## License

This project is open source and available under the MIT License.