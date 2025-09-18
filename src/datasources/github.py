from __future__ import annotations

from typing import Optional


class GitHubClient:
    def __init__(self, base_url: Optional[str], token: Optional[str]) -> None:
        self.base_url = (base_url or "https://api.github.com").rstrip('/')
        self.token = token


