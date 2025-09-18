from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import Collector


class CollectorRegistry:
    def __init__(self) -> None:
        self._collectors: Dict[str, Type[Collector]] = {}

    def register_collector(self, name: str, collector_cls: Type[Collector]) -> None:
        key = name.strip().lower()
        self._collectors[key] = collector_cls

    def get_collector(self, name: str) -> Optional[Type[Collector]]:
        return self._collectors.get(name.strip().lower())

    def list_collectors(self) -> List[str]:
        return sorted(self._collectors.keys())


registry = CollectorRegistry()


