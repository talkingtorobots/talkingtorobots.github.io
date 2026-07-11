"""Author name normalization and HTML rendering."""
from __future__ import annotations

from pylatexenc.latex2text import LatexNodes2Text

_LATEX_TO_TEXT = LatexNodes2Text()

def normalize(name: str) -> str:
    """Convert LaTeX accents/escapes and grouping braces to plain unicode text."""
    return _LATEX_TO_TEXT.latex_to_text(name).strip()

def render_author_html(name: str, websites: dict[str, str],
                       students: set[str], pi: str = "Yonatan Bisk") -> str:
    """Render one normalized author as HTML — exact match, never substring."""
    name = normalize(name)
    html = f'<span class="name">{name}</span>' if name == pi or name in students else name
    if name in websites:
        return f'<a href="{websites[name]}">{html}</a>'
    return html

def render_authors(names: list[str], websites: dict[str, str],
                   students: set[str], pi: str = "Yonatan Bisk") -> str:
    return ", ".join(render_author_html(n, websites, students, pi) for n in names)
