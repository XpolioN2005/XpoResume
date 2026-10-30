import json
import re
from pathlib import Path
from typing import Tuple

from src.models import (
    Metadata,
    ResumeDocument,
    Section,
    Subsection,
    Paragraph,
    ListItem,
    Span,
)

_METADATA_DELIMITER = "---"

_INLINE_RE = re.compile(
    r"\*\*(?P<bold>.+?)\*\*"
    r"|`(?P<code>.+?)`"
    r"|\[(?P<link_text>.+?)\]\((?P<link_url>.+?)\)"
    r"|\*(?P<italic>.+?)\*"
)


def parse_inline(text: str) -> list:
    spans = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            spans.append(Span(text=text[pos:m.start()]))
        if m.group("bold") is not None:
            spans.append(Span(text=m.group("bold"), bold=True))
        elif m.group("code") is not None:
            spans.append(Span(text=m.group("code"), code=True))
        elif m.group("link_text") is not None:
            spans.append(Span(text=m.group("link_text"), url=m.group("link_url")))
        elif m.group("italic") is not None:
            spans.append(Span(text=m.group("italic"), italic=True))
        pos = m.end()
    if pos < len(text):
        spans.append(Span(text=text[pos:]))
    return spans


def _strip_trailing_commas(text: str) -> str:
    """Remove trailing commas in JSON objects/arrays so json.loads accepts them."""
    result = []
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if escape:
            result.append(ch)
            escape = False
            continue
        if ch == "\\" and in_string:
            result.append(ch)
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if ch == "," and not in_string:
            # Look ahead to next non-whitespace char
            j = i + 1
            while j < len(text) and text[j] in " \t\n\r":
                j += 1
            if j < len(text) and text[j] in "}]":
                continue  # drop trailing comma
        result.append(ch)
    return "".join(result)


def _parse_metadata_block(text: str) -> Tuple[dict, str]:
    parts = text.split(_METADATA_DELIMITER)
    if len(parts) >= 3:
        metadata_text = _strip_trailing_commas(parts[1].strip())
        body = _METADATA_DELIMITER.join(parts[2:])
        try:
            metadata_dict = json.loads(metadata_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON metadata: {exc}") from exc
        if not isinstance(metadata_dict, dict):
            raise ValueError("Invalid JSON metadata: expected an object")
        return metadata_dict, body
    return {}, text


def parse_markdown(body: str) -> list:
    sections = []
    current_section = None
    current_subsection = None
    paragraph_lines = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            text = " ".join(line.strip() for line in paragraph_lines if line.strip())
            if text:
                target = current_subsection if current_subsection is not None else current_section
                if target is not None:
                    target.content.append(Paragraph(spans=parse_inline(text)))
            paragraph_lines = []

    for raw_line in body.splitlines():
        line = raw_line.rstrip("\n")

        heading = re.match(r"^#\s+(.+)$", line)
        if heading:
            flush_paragraph()
            current_subsection = None
            current_section = Section(title=heading.group(1).strip())
            sections.append(current_section)
            continue

        subheading = re.match(r"^##\s+(.+)$", line)
        if subheading:
            flush_paragraph()
            current_subsection = Subsection(title=subheading.group(1).strip())
            if current_section is not None:
                current_section.content.append(current_subsection)
            else:
                current_section = Section(title="")
                current_section.content.append(current_subsection)
                sections.append(current_section)
            continue

        bullet = re.match(r"^-\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            item = ListItem(spans=parse_inline(bullet.group(1).strip()))
            target = current_subsection if current_subsection is not None else current_section
            if target is not None:
                target.content.append(item)
            continue

        if line.strip() == "":
            flush_paragraph()
            continue

        paragraph_lines.append(line)

    flush_paragraph()
    return sections


def _parse_margin(value, default: float) -> float:
    if value is None:
        return default
    try:
        result = float(value)
        if result < 0:
            return default
        return result
    except (TypeError, ValueError):
        return default


def parse_file(path: Path) -> ResumeDocument:
    text = Path(path).read_text(encoding="utf-8")
    metadata_dict, body = _parse_metadata_block(text)

    supported = {
        "name", "title", "email", "phone", "location",
        "github", "linkedin", "portfolio", "primary_color", "accent_color",
        "url_color",
        "text_color",
        "margin_left", "margin_right", "margin_top", "margin_bottom",
    }
    metadata_dict = {k: v for k, v in metadata_dict.items() if k in supported}

    metadata = Metadata(
        name=metadata_dict.get("name", "") or "",
        title=metadata_dict.get("title", "") or "",
        email=metadata_dict.get("email"),
        phone=metadata_dict.get("phone"),
        location=metadata_dict.get("location"),
        github=metadata_dict.get("github"),
        linkedin=metadata_dict.get("linkedin"),
        portfolio=metadata_dict.get("portfolio"),
        primary_color=metadata_dict.get("primary_color", "#0BBF89") or "#0BBF89",
        accent_color=metadata_dict.get("accent_color", "#0E1015") or "#0E1015",
        url_color=metadata_dict.get("url_color", "#0000EE") or "#0000EE",
        text_color=metadata_dict.get("text_color", "#1a1a1a") or "#1a1a1a",
        margin_left=_parse_margin(metadata_dict.get("margin_left"), 54.0),
        margin_right=_parse_margin(metadata_dict.get("margin_right"), 54.0),
        margin_top=_parse_margin(metadata_dict.get("margin_top"), 54.0),
        margin_bottom=_parse_margin(metadata_dict.get("margin_bottom"), 54.0),
    )

    sections = parse_markdown(body)
    return ResumeDocument(metadata=metadata, sections=sections)
