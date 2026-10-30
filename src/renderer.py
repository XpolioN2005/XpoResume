import xml.sax.saxutils as saxutils
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
)

from src.models import (
    ResumeDocument,
    Section,
    Subsection,
    Paragraph as ModelParagraph,
    ListItem as ModelListItem,
)


def _escape(text: str) -> str:
    return saxutils.escape(text or "")


def _spans_to_markup(spans, url_color: str) -> str:
    parts = []
    for span in spans:
        text = _escape(span.text)
        if span.code:
            text = f'<font face="Courier">{text}</font>'
        if span.bold:
            text = f"<b>{text}</b>"
        if span.italic:
            text = f"<i>{text}</i>"
        if span.url:
            text = f'<a href="{_escape(span.url)}" color="{url_color}"><u>{text}</u></a>'
        parts.append(text)
    return "".join(parts)


def _color(value: str, fallback: str) -> str:
    try:
        HexColor(value or fallback)
    except Exception:
        return fallback
    return value or fallback


def _heading_with_date(title: str, date: str | None, style, left_margin: float = 0, available_width: float | None = None) -> list:
    """Return flowables for a heading, with an optional right-aligned date."""
    if date:
        title_par = Paragraph(title, style)
        date_style = ParagraphStyle(
            "date_right", parent=style, alignment=2,
        )
        date_par = Paragraph(date, date_style)
        if available_width is None:
            col_widths = [4.2 * inch, 2.0 * inch]
        else:
            date_col = 1.5 * inch
            title_col = max(available_width - date_col - 10, 1.0 * inch)
            col_widths = [title_col, date_col]
        tbl = Table([[title_par, date_par]], colWidths=col_widths)
        left_pad = left_margin + (getattr(style, "leftIndent", 0) or 0)
        tbl.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), left_pad),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEADING", (0, 0), (-1, -1), style.leading),
        ]))
        return [tbl]
    return [Paragraph(title, style)]


def _render_skills_section(section, subsection_style, body_style, bullet_style, url_color, left_margin: float = 0, available_width: float | None = None):
    """Render a Skills section with subsections laid out in 2 columns."""
    subsections = [item for item in section.content if isinstance(item, Subsection)]
    if not subsections:
        return _content_flowables(section.content, body_style, bullet_style, subsection_style, url_color, left_margin, available_width)

    flowables = []
    if available_width is not None:
        col_width = (available_width - 12) / 2
    else:
        col_width = 3.3 * inch

    cell_title_style = ParagraphStyle(
        "skill_cell_title", parent=subsection_style, spaceBefore=0, spaceAfter=2,
    )
    cell_body_style = ParagraphStyle(
        "skill_cell_body", parent=body_style, leftIndent=25, spaceBefore=0, spaceAfter=1,
    )

    def _cell_flowables(sub):
        cells = []
        title = sub.title
        date = None
        if " | " in title:
            parts = title.split(" | ", 1)
            title = parts[0].strip()
            date = parts[1].strip()
        cells.extend(_heading_with_date(title, date, cell_title_style, 0, None))
        for subitem in sub.content:
            if isinstance(subitem, ModelParagraph):
                cells.append(Paragraph(_spans_to_markup(subitem.spans, url_color), cell_body_style))
            elif isinstance(subitem, ModelListItem):
                cells.append(Paragraph("• " + _spans_to_markup(subitem.spans, url_color), bullet_style))
        return cells

    i = 0
    while i < len(subsections):
        left = subsections[i]
        right = subsections[i + 1] if i + 1 < len(subsections) else None
        left_cells = _cell_flowables(left)
        right_cells = _cell_flowables(right) if right else [Spacer(1, 1)]

        max_rows = max(len(left_cells), len(right_cells))
        left_cells += [Spacer(1, 2)] * (max_rows - len(left_cells))
        right_cells += [Spacer(1, 2)] * (max_rows - len(right_cells))

        table_data = [[l, r] for l, r in zip(left_cells, right_cells)]
        tbl = Table(table_data, colWidths=[col_width, col_width])
        tbl.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        flowables.append(tbl)
        flowables.append(Spacer(1, 8))
        i += 2
    return flowables


def _content_flowables(content, body_style, bullet_style, subsection_style, url_color, left_margin: float = 0, available_width: float | None = None):
    flowables = []
    i = 0
    while i < len(content):
        item = content[i]
        if isinstance(item, Subsection):
            title = item.title
            date = None
            if " | " in title:
                parts = title.split(" | ", 1)
                title = parts[0].strip()
                date = parts[1].strip()
            flowables.extend(_heading_with_date(title, date, subsection_style, left_margin, available_width))
            i += 1
            for subitem in item.content:
                if isinstance(subitem, ModelParagraph):
                    flowables.append(Paragraph(_spans_to_markup(subitem.spans, url_color), body_style))
                elif isinstance(subitem, ModelListItem):
                    flowables.append(Paragraph("• " + _spans_to_markup(subitem.spans, url_color), bullet_style))
        elif isinstance(item, ModelListItem):
            batch = []
            while i < len(content) and isinstance(content[i], ModelListItem):
                batch.append(content[i])
                i += 1
            flowables.append(ListFlowable(
                [Paragraph(_spans_to_markup(b.spans, url_color), bullet_style) for b in batch],
                bulletType="bullet",
                leftIndent=16,
                bulletFontSize=9,
                spaceAfter=4,
            ))
        elif isinstance(item, ModelParagraph):
            flowables.append(Paragraph(_spans_to_markup(item.spans, url_color), body_style))
            i += 1
        else:
            i += 1
    return flowables


def render(document: ResumeDocument, output_path) -> None:
    meta = document.metadata
    primary_color = _color(meta.primary_color, "#0BBF89")
    accent_color = _color(meta.accent_color, "#0E1015")
    url_color = _color(meta.url_color, "#0000EE")
    text_color = _color(getattr(meta, "text_color", "#1a1a1a"), "#1a1a1a")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=meta.margin_left,
        rightMargin=meta.margin_right,
        topMargin=meta.margin_top,
        bottomMargin=meta.margin_bottom,
        title=meta.name or "Resume",
        author=meta.name or "Resume",
    )

    name_style = ParagraphStyle(
        "name", fontName="Helvetica-Bold", fontSize=21, leading=24,
        textColor=HexColor(primary_color), alignment=1,
    )
    title_style = ParagraphStyle(
        "title", fontName="Helvetica", fontSize=12, leading=15,
        textColor=HexColor(accent_color), alignment=1, spaceAfter=6,
    )
    contact_style = ParagraphStyle(
        "contact", fontName="Helvetica", fontSize=8.4, leading=11,
        textColor=HexColor(text_color), alignment=1,
    )
    social_style = ParagraphStyle(
        "social", fontName="Helvetica", fontSize=8.4, leading=11,
        textColor=HexColor(text_color), alignment=1, spaceAfter=5,
    )
    section_style = ParagraphStyle(
        "section", fontName="Helvetica-Bold", fontSize=15, leading=18,
        textColor=HexColor(primary_color), spaceBefore=10, spaceAfter=7,
        leftIndent=10,
    )
    subsection_style = ParagraphStyle(
        "subsection", fontName="Helvetica-Bold", fontSize=13, leading=16,
        textColor=HexColor(accent_color), spaceBefore=5, spaceAfter=7,
    )
    body_style = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=9.5, leading=13.5,
        textColor=HexColor(text_color), spaceAfter=5,
        leftIndent=25,
    )
    bullet_style = ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=9.5, leading=13.5,
        textColor=HexColor(text_color), leftIndent=35, spaceAfter=2,
    )

    story = []

    # Header (centered)
    story.append(Paragraph(meta.name, name_style))
    if meta.title:
        story.append(Paragraph(meta.title, title_style))

    contact_parts = []
    if meta.location:
        contact_parts.append(meta.location)
    if meta.email:
        contact_parts.append(meta.email)
    if meta.phone:
        contact_parts.append(meta.phone)
    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), contact_style))

    social_items = []
    if meta.github:
        social_items.append(f'<a href="{_escape(meta.github)}" color="{url_color}"><u>GitHub</u></a>')
    if meta.linkedin:
        social_items.append(f'<a href="{_escape(meta.linkedin)}" color="{url_color}"><u>LinkedIn</u></a>')
    if meta.portfolio:
        social_items.append(f'<a href="{_escape(meta.portfolio)}" color="{url_color}"><u>Portfolio</u></a>')
    if social_items:
        story.append(Paragraph(" | ".join(social_items), social_style))

    story.append(Spacer(1, 10))

    # Body content - render sequentially, page breaks only on natural overflow
    available_width = A4[0] - meta.margin_left - meta.margin_right
    for section in document.sections:
        story.append(Paragraph(section.title, section_style))
        if section.title.strip().lower() == "skills":
            story.extend(_render_skills_section(section, subsection_style, body_style, bullet_style, url_color, meta.margin_left, available_width))
        else:
            story.extend(_content_flowables(
                section.content, body_style, bullet_style, subsection_style, url_color, meta.margin_left, available_width
            ))

    doc.build(story)
