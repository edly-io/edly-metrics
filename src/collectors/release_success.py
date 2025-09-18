from __future__ import annotations

from typing import Dict, Any, List
from datetime import datetime, timezone

import pandas as pd

from ..base import Collector
from ..config import AppConfig
from ..registry import registry
from ..datasources.gitlab import GitLabClient


def _to_iso(date_str: str) -> str:
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.replace(tzinfo=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


class ReleaseSuccessCollector(Collector):
    def collect(self) -> pd.DataFrame:
        cfg: AppConfig = self.config
        base_url = cfg.gitlab_base_url
        client = GitLabClient(base_url=base_url, token=cfg.gitlab_token)

        created_after = _to_iso(cfg.date_from) if cfg.date_from else None
        created_before = _to_iso(cfg.date_to) if cfg.date_to else None

        projects = client.list_projects()
        rows: List[Dict[str, Any]] = []
        for project in projects:
            project_id = project['id']
            project_name = project['name']
            pipelines = client.list_tag_pipelines(
                project_id=project_id,
                created_after_iso=created_after,
                created_before_iso=created_before,
            )
            for p in pipelines:
                rows.append({
                    'Project': project_name,
                    'Version': p.get('ref', ''),
                    'Release Date': p.get('created_at', ''),
                    'Status': p.get('status', ''),
                })

        df = pd.DataFrame(rows, columns=['Project', 'Version', 'Release Date', 'Status'])
        if 'Release Date' in df.columns and not df.empty:
            df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
            df['Release Date'] = df['Release Date'].dt.strftime('%b %d, %Y')
        return df


registry.register_collector('release_success', ReleaseSuccessCollector)


