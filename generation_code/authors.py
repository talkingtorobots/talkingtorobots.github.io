"""Author name normalization and HTML rendering."""
from __future__ import annotations

from pylatexenc.latex2text import LatexNodes2Text

_LATEX_TO_TEXT = LatexNodes2Text()

def normalize(name: str) -> str:
    """Convert LaTeX accents/escapes and grouping braces to plain unicode text."""
    return _LATEX_TO_TEXT.latex_to_text(name).strip()

def render_author_html(name: str, websites: dict[str, str],
                       students: set[str], pi: str = "Yonatan Bisk",
                       pubnames: dict[str, str] | None = None) -> str:
    """Render one normalized author as HTML — exact match, never substring.

    Bolding and homepage links key off `name`; only the visible byline is swapped
    for a `pubnames` entry, so a person published under a different name ordering
    still resolves to their record.
    """
    name = normalize(name)
    shown = (pubnames or {}).get(name, name)
    html = f'<span class="name">{shown}</span>' if name == pi or name in students else shown
    if name in websites:
        return f'<a href="{websites[name]}">{html}</a>'
    return html

def render_authors(names: list[str], websites: dict[str, str],
                   students: set[str], pi: str = "Yonatan Bisk",
                   pubnames: dict[str, str] | None = None) -> str:
    return ", ".join(render_author_html(n, websites, students, pi, pubnames) for n in names)
