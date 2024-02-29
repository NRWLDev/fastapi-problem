from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class CorsConfiguration:
    allow_origins: list[str]
    allow_methods: list[str]
    allow_headers: list[str]
    allow_credentials: bool
