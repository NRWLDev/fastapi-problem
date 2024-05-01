from __future__ import annotations

import http


def convert_status_code(status_code: int) -> tuple[str, str]:
    """Convert an HTTP status code into a (title, type)."""
    title = http.HTTPStatus(status_code).phrase
    code = "-".join(title.lower().split())

    return title, f"http-{code}"
