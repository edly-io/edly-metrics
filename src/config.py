from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


@dataclass
class AppConfig:
    output: str = "./files/out.csv"
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    gitlab_base_url: Optional[str] = None

    gitlab_token: Optional[str] = None
    github_token: Optional[str] = None
    azure_pat: Optional[str] = None


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(key)
    return val if val not in (None, "") else default


def load_config(config_path: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    load_dotenv()
    data: Dict[str, Any] = {}

    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.endswith(('.yml', '.yaml')):
                data = yaml.safe_load(f) or {}
            else:
                import json
                data = json.load(f)

    overrides = overrides or {}
    data.update({k: v for k, v in overrides.items() if v is not None})

    cfg = AppConfig(
        output=data.get("output", "./files/out.csv"),
        date_from=data.get("date_from"),
        date_to=data.get("date_to"),
        gitlab_base_url=data.get("gitlab_base_url") or data.get("base_url"),
        gitlab_token=data.get("gitlab_token") or _env("GITLAB_TOKEN"),
        github_token=data.get("github_token") or _env("GITHUB_TOKEN"),
        azure_pat=data.get("azure_pat") or _env("AZURE_PAT"),
    )
    return cfg


