from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Metadata:
    name: str
    title: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    primary_color: str = "#0BBF89"
    accent_color: str = "#0E1015"
    url_color: str = "#0000EE"
    text_color: str = "#1a1a1a"
    margin_left: float = 54.0
    margin_right: float = 54.0
    margin_top: float = 54.0
    margin_bottom: float = 54.0


@dataclass
class Span:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    url: Optional[str] = None


@dataclass
class Paragraph:
    spans: List[Span] = field(default_factory=list)


@dataclass
class ListItem:
    spans: List[Span] = field(default_factory=list)


@dataclass
class Subsection:
    title: str
    content: List = field(default_factory=list)


@dataclass
class Section:
    title: str
    content: List = field(default_factory=list)


@dataclass
class ResumeDocument:
    metadata: Metadata
    sections: List[Section] = field(default_factory=list)
