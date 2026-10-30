import re
from typing import List, Tuple

from src.models import ResumeDocument, Section, Subsection, Paragraph, ListItem

_HEX_COLOR_RE = re.compile(r"^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$")


def validate(document: ResumeDocument) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    meta = document.metadata

    if not meta.name:
        errors.append("Missing required metadata field: name")
    if not meta.title:
        errors.append("Missing required metadata field: title")

    for field_name, value in (("primary_color", meta.primary_color), ("accent_color", meta.accent_color),
                              ("url_color", meta.url_color), ("text_color", meta.text_color)):
        if not _HEX_COLOR_RE.match(value or ""):
            errors.append(f"Invalid color value for {field_name}: {value}")

    for field_name, value in (("margin_left", meta.margin_left), ("margin_right", meta.margin_right),
                              ("margin_top", meta.margin_top), ("margin_bottom", meta.margin_bottom)):
        if not isinstance(value, (int, float)) or value < 0:
            errors.append(f"Invalid margin value for {field_name}: {value}")

    if not meta.email:
        warnings.append("Email is not specified.")
    if not meta.phone:
        warnings.append("Phone is not specified.")
    if not meta.location:
        warnings.append("Location is not specified.")
    if not meta.github:
        warnings.append("GitHub is not specified.")
    if not meta.linkedin:
        warnings.append("LinkedIn is not specified.")
    if not meta.portfolio:
        warnings.append("Portfolio is not specified.")

    if not document.sections:
        errors.append("Invalid Markdown structure: no sections found")
    else:
        for section in document.sections:
            if not section.title:
                errors.append("Invalid Markdown structure: section missing title")
            if not section.content:
                warnings.append(f"Section '{section.title or 'Untitled'}' is empty.")
            for item in section.content:
                if isinstance(item, Subsection):
                    if not item.title:
                        errors.append("Invalid Markdown structure: subsection missing title")
                    if not item.content:
                        warnings.append(f"Subsection '{item.title or 'Untitled'}' is empty.")
                    for subitem in item.content:
                        if isinstance(subitem, Paragraph) and not subitem.spans:
                            warnings.append("Empty content found.")
                        elif isinstance(subitem, ListItem) and not subitem.spans:
                            warnings.append("Empty content found.")
                elif isinstance(item, Paragraph) and not item.spans:
                    warnings.append("Empty content found.")
                elif isinstance(item, ListItem) and not item.spans:
                    warnings.append("Empty content found.")

    return errors, warnings
