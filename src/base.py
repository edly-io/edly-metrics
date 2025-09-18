from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from .config import AppConfig


class Collector(ABC):
    def __init__(self, config: AppConfig):
        self.config = config

    @abstractmethod
    def collect(self) -> pd.DataFrame:
        ...

    def export(self, df: pd.DataFrame, output_path: str) -> None:
        if output_path.lower().endswith(".xlsx"):
            df.to_excel(output_path, index=False)
        else:
            df.to_csv(output_path, index=False)


