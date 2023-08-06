import bleach
from markdown import Markdown


def convert_md_to_html(raw_markdown_text: str) -> str:
    markdowner = Markdown(extensions=["tables", "footnotes"])
    html = markdowner.convert(raw_markdown_text)
    allowed = [
        "blockquote",
        "h1",
        "h2",
        "h3",
        "b",
        "strong",
        "i",
        "em",
        "p",
        "sup",
        "a",
        "ol",
        "ul",
        "li",
        "table",
        "thead",
        "tbody",
        "th",
        "tr",
        "td",
        "pre",
        "mark",
    ]
    return bleach.clean(html, tags=allowed)
