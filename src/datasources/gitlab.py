from __future__ import annotations

from typing import Any, Dict, List, Optional
import time
import re

import requests


class GitLabClient:
    DEFAULT_TIMEOUT = 20
    VERSION_TAG_PATTERN = re.compile(r'^(?:v?\d+\.\d+\.\d+|\d{4}\.\d{2})')

    def __init__(self, base_url: str, token: Optional[str]) -> None:
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Private-Token'] = token
        self.session.headers.update(headers)

    def list_projects(self) -> List[Dict[str, Any]]:
        projects: List[Dict[str, Any]] = []
        page = 1
        per_page = 100
        while True:
            params = {
                'page': page,
                'per_page': per_page,
                'simple': 'true',
                'order_by': 'name',
                'sort': 'asc',
            }
            resp = self.session.get(f"{self.base_url}/projects", params=params, timeout=self.DEFAULT_TIMEOUT)
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            projects.extend(batch)
            page += 1
            time.sleep(0.1)
        return projects

    def list_tag_pipelines(
        self,
        project_id: int,
        created_after_iso: Optional[str] = None,
        created_before_iso: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        pipelines: List[Dict[str, Any]] = []
        page = 1
        per_page = 100
        while True:
            params: Dict[str, Any] = {
                'page': page,
                'per_page': per_page,
                'source': 'push',
                'order_by': 'updated_at',
                'sort': 'desc',
                'scope': 'tags',
            }
            # These filters don't seem to be working reference:
            # https://docs.gitlab.com/api/pipelines/#list-project-pipelines
            if created_after_iso:
                params['created_after'] = created_after_iso
            if created_before_iso:
                params['created_before'] = created_before_iso

            resp = self.session.get(
                f"{self.base_url}/projects/{project_id}/pipelines",
                params=params,
                timeout=self.DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            # tag_pipelines = [p for p in batch if self._is_version_tag(p.get('ref', ''))]
            pipelines.extend(batch)
            page += 1
            time.sleep(0.05)
            if len(batch) < per_page:
                break
        return pipelines

    # def _is_version_tag(self, ref: str) -> bool:
    #     if not ref:
    #         return False
    #     return bool(self.VERSION_TAG_PATTERN.match(ref.lower()))


