from markupsafe import escape


def to_safe_html(s) -> str:
    return str(escape(s))
