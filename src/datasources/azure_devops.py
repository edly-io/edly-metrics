from __future__ import annotations

from typing import Optional


class AzureDevOpsClient:
    def __init__(self, base_url: Optional[str], pat: Optional[str]) -> None:
        self.base_url = (base_url or "https://dev.azure.com").rstrip('/')
        self.pat = pat


