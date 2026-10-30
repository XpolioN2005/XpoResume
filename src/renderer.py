import xml.sax.saxutils as saxutils

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from src.models import (
    ResumeDocument,
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
            text = (
                f'<a href="{_escape(span.url)}" '
                f'color="{url_color}"><u>{text}</u></a>'
            )

        parts.append(text)

    return "".join(parts)


def _color(value: str, fallback: str) -> str:
    try:
        HexColor(value or fallback)
    except Exception:
        return fallback

    return value or fallback


def _split_title_date(title: str) -> tuple[str, str | None]:
    if " | " not in title:
        return title.strip(), None

    name, date = title.split(" | ", 1)
    return name.strip(), date.strip()


def _heading_with_date(
    title: str,
    date: str | None,
    style,
    available_width: float,
) -> list:
    if not date:
        return [Paragraph(_escape(title), style)]

    date_style = ParagraphStyle(
        "date_right",
        parent=style,
        alignment=2,
        leftIndent=0,
        rightIndent=0,
    )

    title_paragraph = Paragraph(_escape(title), style)
    date_paragraph = Paragraph(_escape(date), date_style)

    date_width = 1.5 * inch
    title_width = max(
        available_width - date_width,
        1.0 * inch,
    )

    table = Table(
        [[title_paragraph, date_paragraph]],
        colWidths=[title_width, date_width],
    )

    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    return [table]


def _render_bullet(
    item: ModelListItem,
    bullet_style,
    url_color: str,
) -> Paragraph:
    return Paragraph(
        f"• {_spans_to_markup(item.spans, url_color)}",
        bullet_style,
    )


def _render_subsection(
    subsection: Subsection,
    subsection_style,
    body_style,
    bullet_style,
    url_color: str,
    available_width: float,
) -> list:
    flowables = []

    title, date = _split_title_date(subsection.title)

    flowables.extend(
        _heading_with_date(
            title,
            date,
            subsection_style,
            available_width,
        )
    )

    for item in subsection.content:
        if isinstance(item, ModelParagraph):
            flowables.append(
                Paragraph(
                    _spans_to_markup(item.spans, url_color),
                    body_style,
                )
            )

        elif isinstance(item, ModelListItem):
            flowables.append(
                _render_bullet(
                    item,
                    bullet_style,
                    url_color,
                )
            )

    return flowables


def _content_flowables(
    content,
    body_style,
    bullet_style,
    subsection_style,
    url_color,
    available_width,
) -> list:
    flowables = []

    for item in content:
        if isinstance(item, Subsection):
            flowables.extend(
                _render_subsection(
                    item,
                    subsection_style,
                    body_style,
                    bullet_style,
                    url_color,
                    available_width,
                )
            )

        elif isinstance(item, ModelParagraph):
            flowables.append(
                Paragraph(
                    _spans_to_markup(item.spans, url_color),
                    body_style,
                )
            )

        elif isinstance(item, ModelListItem):
            flowables.append(
                _render_bullet(
                    item,
                    bullet_style,
                    url_color,
                )
            )

    return flowables


def _render_skills_section(
    section,
    subsection_style,
    body_style,
    bullet_style,
    url_color,
    available_width,
) -> list:
    subsections = [
        item
        for item in section.content
        if isinstance(item, Subsection)
    ]

    if not subsections:
        return _content_flowables(
            section.content,
            body_style,
            bullet_style,
            subsection_style,
            url_color,
            available_width,
        )

    flowables = []

    column_gap = 12
    column_width = (available_width - column_gap) / 2

    skill_title_style = ParagraphStyle(
        "skill_title",
        parent=subsection_style,
        spaceBefore=0,
        spaceAfter=2,
    )

    skill_body_style = ParagraphStyle(
        "skill_body",
        parent=body_style,
        spaceBefore=0,
        spaceAfter=1,
    )

    skill_bullet_style = ParagraphStyle(
        "skill_bullet",
        parent=bullet_style,
        spaceBefore=0,
        spaceAfter=1,
    )

    def render_cell(subsection: Subsection) -> list:
        cells = []

        title, date = _split_title_date(subsection.title)

        cells.extend(
            _heading_with_date(
                title,
                date,
                skill_title_style,
                column_width,
            )
        )

        for item in subsection.content:
            if isinstance(item, ModelParagraph):
                cells.append(
                    Paragraph(
                        _spans_to_markup(
                            item.spans,
                            url_color,
                        ),
                        skill_body_style,
                    )
                )

            elif isinstance(item, ModelListItem):
                cells.append(
                    _render_bullet(
                        item,
                        skill_bullet_style,
                        url_color,
                    )
                )

        return cells

    for index in range(0, len(subsections), 2):
        left = render_cell(subsections[index])

        if index + 1 < len(subsections):
            right = render_cell(subsections[index + 1])
        else:
            right = [Spacer(1, 1)]

        row_count = max(len(left), len(right))

        left.extend(
            Spacer(1, 1)
            for _ in range(row_count - len(left))
        )

        right.extend(
            Spacer(1, 1)
            for _ in range(row_count - len(right))
        )

        table = Table(
            list(zip(left, right)),
            colWidths=[column_width, column_width],
        )

        table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        flowables.append(table)
        flowables.append(Spacer(1, 6))

    return flowables


def render(document: ResumeDocument, output_path) -> None:
    meta = document.metadata

    primary_color = _color(
        meta.primary_color,
        "#0BBF89",
    )

    accent_color = _color(
        meta.accent_color,
        "#0E1015",
    )

    url_color = _color(
        meta.url_color,
        "#0000EE",
    )

    text_color = _color(
        getattr(meta, "text_color", "#1a1a1a"),
        "#1a1a1a",
    )

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
        "name",
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=24,
        textColor=HexColor(primary_color),
        alignment=1,
    )

    title_style = ParagraphStyle(
        "title",
        fontName="Helvetica",
        fontSize=12,
        leading=15,
        textColor=HexColor(accent_color),
        alignment=1,
        spaceAfter=6,
    )

    contact_style = ParagraphStyle(
        "contact",
        fontName="Helvetica",
        fontSize=8.4,
        leading=11,
        textColor=HexColor(text_color),
        alignment=1,
    )

    social_style = ParagraphStyle(
        "social",
        fontName="Helvetica",
        fontSize=8.4,
        leading=11,
        textColor=HexColor(text_color),
        alignment=1,
        spaceAfter=5,
    )

    section_style = ParagraphStyle(
        "section",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=HexColor(primary_color),
        spaceBefore=10,
        spaceAfter=5,
        leftIndent=0,
    )

    subsection_style = ParagraphStyle(
        "subsection",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=HexColor(accent_color),
        spaceBefore=5,
        spaceAfter=3,
        leftIndent=10,
    )

    body_style = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=HexColor(text_color),
        spaceAfter=3,
        leftIndent=20,
    )

    bullet_style = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=HexColor(text_color),
        leftIndent=30,
        firstLineIndent=-10,
        spaceAfter=1,
    )

    story = []

    story.append(
        Paragraph(
            _escape(meta.name),
            name_style,
        )
    )

    if meta.title:
        story.append(
            Paragraph(
                _escape(meta.title),
                title_style,
            )
        )

    contact_parts = []

    if meta.location:
        contact_parts.append(
            _escape(meta.location)
        )

    if meta.email:
        contact_parts.append(
            _escape(meta.email)
        )

    if meta.phone:
        contact_parts.append(
            _escape(meta.phone)
        )

    if contact_parts:
        story.append(
            Paragraph(
                " | ".join(contact_parts),
                contact_style,
            )
        )

    social_items = []

    if meta.github:
        social_items.append(
            f'<a href="{_escape(meta.github)}" '
            f'color="{url_color}"><u>GitHub</u></a>'
        )

    if meta.linkedin:
        social_items.append(
            f'<a href="{_escape(meta.linkedin)}" '
            f'color="{url_color}"><u>LinkedIn</u></a>'
        )

    if meta.portfolio:
        social_items.append(
            f'<a href="{_escape(meta.portfolio)}" '
            f'color="{url_color}"><u>Portfolio</u></a>'
        )

    if social_items:
        story.append(
            Paragraph(
                " | ".join(social_items),
                social_style,
            )
        )

    story.append(Spacer(1, 10))

    available_width = (
        A4[0]
        - meta.margin_left
        - meta.margin_right
    )

    for section in document.sections:
        story.append(
            Paragraph(
                _escape(section.title),
                section_style,
            )
        )

        if section.title.strip().lower() == "skills":
            story.extend(
                _render_skills_section(
                    section,
                    subsection_style,
                    body_style,
                    bullet_style,
                    url_color,
                    available_width,
                )
            )
        else:
            story.extend(
                _content_flowables(
                    section.content,
                    body_style,
                    bullet_style,
                    subsection_style,
                    url_color,
                    available_width,
                )
            )

    doc.build(story)
