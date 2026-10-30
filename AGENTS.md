# AGENTS.md

## Project

Resume Compiler v1 is a small Python program that converts a Markdown resume into a formatted PDF.

```text
resume.md -> parse -> validate -> render -> dist/resume.pdf
```

The project is intentionally minimal. Do not add features outside the requirements.

## Goal

Running:

```bash
python resume.py
```

must:

1. Locate `resume.md` in the project directory.
2. Ask for a Markdown file path if it does not exist.
3. Parse the metadata and Markdown content.
4. Validate the document.
5. Generate `dist/resume.pdf`.
6. Create `dist/` if necessary.

## Tech Stack

- Python
- ReportLab
- Python standard library

No other external dependencies.

Use standard-library modules such as:

- `json`
- `pathlib`
- `re`
- `dataclasses`

Do not add PyYAML or a Markdown library.

## Project Structure

```text
resume-compiler/
├── resume.py
├── resume.md
├── requirements.txt
├── src/
│   ├── parser.py
│   ├── models.py
│   ├── validator.py
│   └── renderer.py
└── dist/
    └── resume.pdf
```

`resume.py` is the only user-facing entry point.

## Architecture

```text
resume.py
    |
    +-- parser.py
    |      Markdown -> structured document
    |
    +-- validator.py
    |      validate metadata and document
    |
    +-- renderer.py
           structured document -> PDF
```

Keep these responsibilities separate.

### Parser

Responsible only for:

- Reading the input file.
- Parsing the JSON metadata block.
- Parsing supported Markdown.
- Producing the structured document model.

The parser must not contain PDF or ReportLab logic.

### Models

Define simple data structures representing:

- Resume metadata
- Resume document
- Sections
- Subsections
- Paragraphs
- Lists
- Inline formatted content
- Links

Keep models simple. Do not build a generic Markdown AST.

### Validator

Responsible only for validation.

Errors must stop generation:

- Invalid JSON metadata.
- Missing `name`.
- Missing `title`.
- Invalid color values.
- Invalid Markdown structure.

Warnings should not stop generation:

- Missing contact fields.
- Missing social links.
- Empty sections.
- Empty content.

### Renderer

Responsible only for converting the structured document into a PDF using ReportLab.

It must:

- Use A4.
- Use fixed sensible margins.
- Use fixed typography.
- Render content sequentially.
- Preserve Markdown order.
- Handle multiple pages.
- Handle automatic page breaks.
- Preserve hyperlinks.
- Render selectable text.
- Apply configured colors.

The renderer must not inspect or parse raw Markdown.

## Metadata

The Markdown file begins with a JSON metadata block.

Example:

```json
{
	"name": "Your Name",
	"title": "Software Developer",
	"email": "you@example.com",
	"phone": "+1 555-0100",
	"location": "City, Country",
	"github": "https://github.com/yourusername",
	"linkedin": "https://linkedin.com/in/yourusername",
	"portfolio": "https://yourportfolio.dev",
	"primary_color": "#0BBF89",
	"accent_color": "#0E1015"
}
```

The metadata block is delimited by:

```text
---
{ JSON }
---
```

Supported fields:

- `name` - required
- `title` - required
- `email`
- `phone`
- `location`
- `github`
- `linkedin`
- `portfolio`
- `primary_color`
- `accent_color`

Do not add configuration fields without a requirement for them.

## Markdown

Only support the Markdown required by the project:

- `# Heading`
- `## Heading`
- Paragraphs
- Bullet lists
- Bold
- Italic
- Inline code
- Links

`#` creates a top-level section.

`##` creates a subsection inside the current section.

The Markdown order is authoritative.

Do not reorder sections or impose a resume schema.

Example:

```md
---
{ "name": "Darsan Ghosh", "title": "Game Developer" }
---

# Projects

## OscilloRun

Project description.

# Skills

...

# Experience

## Game Developer

...
```

Must render in exactly that order.

## Header

The PDF starts with metadata information.

Display only fields that exist.

Typical output:

```text
Your Name
Software Developer

City, Country
you@example.com
+1 555-0100
GitHub | LinkedIn | Portfolio
```

Links must be clickable.

## Styling

Use a clean, professional fixed layout.

Hierarchy:

```text
Name
Title
Contact information

# Section
## Subsection
Body
Lists
```

Use:

- `primary_color` for the name and main section headings.
- `accent_color` for links and secondary visual details.
- Fixed sensible styling for everything else.

Do not add theme systems, templates, layout configuration, or font configuration.

## Dependency Policy

Keep dependencies minimal.

Required external dependency:

```text
reportlab
```

Everything else should use the Python standard library.

Do not introduce a dependency for functionality that can reasonably be implemented with the standard library.

## Error Handling

Errors should be clear and actionable.

Example:

```text
ERROR: Missing required metadata field: name
```

Warnings should be clearly marked:

```text
WARNING: LinkedIn is not specified.
```

Successful generation should end with:

```text
Generated: dist/resume.pdf
```

## Implementation Rules

- Keep the implementation small.
- Prefer straightforward code over abstractions.
- Do not over-engineer the parser.
- Do not implement unsupported Markdown.
- Do not implement a generic Markdown renderer.
- Do not add a dependency for JSON or Markdown parsing.
- Do not add CLI commands or subcommands.
- Do not add a web interface.
- Do not add an editor.
- Do not add ATS functionality.
- Do not add job matching.
- Do not add AI functionality.
- Do not generate `.txt` output.
- Do not add resume templates.
- Do not add configurable page sizes.
- Do not add configurable layouts.
- Do not add configurable fonts.

The compiler should remain a small Markdown-to-PDF tool.
