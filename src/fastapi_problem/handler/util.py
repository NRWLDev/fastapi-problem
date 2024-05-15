from __future__ import annotations

import http


def convert_status_code(status_code: int) -> tuple[str, str]:
    """Convert an HTTP status code into a (title, type)."""
    title = http.HTTPStatus(status_code).phrase
    type_ = "-".join(title.lower().split())

    return title, f"http-{type_}"
