# XpoResume

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![GitHub Stars](https://img.shields.io/github/stars/XpolioN2005/XpoResume?style=flat)](https://github.com/XpolioN2005/XpoResume/stargazers) [![GitHub Issues](https://img.shields.io/github/issues/XpolioN2005/XpoResume)](https://github.com/XpolioN2005/XpoResume/issues)

XpoResume is a Markdown-based resume generator that converts a structured resume file into a PDF.

## Requirements

- Python 3.10+
- pip

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/XpolioN2005/XpoResume.git
cd XpoResume

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

On Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Creating a Resume

Use `resume.example.md` as the reference for the supported resume format.

Copy it to create your own resume:

```bash
cp resume.example.md resume.md
```

On Windows PowerShell:

```powershell
Copy-Item resume.example.md resume.md
```

Edit `resume.md` with your own information.

The example file defines the expected structure and available fields. Keep the structure intact when adding or modifying resume content.

## Generate the PDF

Run:

```bash
python resume.py
```

The generated resume will be written to:

```text
dist/resume.pdf
```

## Project Structure

```text
XpoResume/
├── resume.py              # CLI entry point
├── resume.example.md      # Resume format reference
├── requirements.txt       # Python dependencies
├── src/
│   ├── models.py          # Resume data models
│   ├── parser.py          # Markdown parsing
│   ├── renderer.py        # PDF rendering
│   ├── validator.py       # Resume validation
│   └── __init__.py
└── dist/
    └── resume.pdf         # Generated PDF
```

## Workflow

```text
resume.md
    |
    v
Parser
    |
    v
Validation
    |
    v
Resume Model
    |
    v
PDF Renderer
    |
    v
dist/resume.pdf
```

## Notes

`resume.example.md` is a template/reference file. It is not intended to be edited directly.

Create your own `resume.md` from the example and use that file as the input for generating your resume.
