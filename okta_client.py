"""Okta 데이터 조회용 읽기 전용 API 클라이언트.

그룹 멤버 조회, 앱 할당 현황 조회에 사용합니다.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OKTA_DOMAIN = os.environ.get("OKTA_DOMAIN", "").rstrip("/")
OKTA_API_TOKEN = os.environ.get("OKTA_API_TOKEN", "")


class OktaClient:
    def __init__(self, domain: str = OKTA_DOMAIN, token: str = OKTA_API_TOKEN):
        if not domain or not token:
            raise ValueError("OKTA_DOMAIN, OKTA_API_TOKEN 환경변수가 필요합니다.")
        self.base = domain + "/api/v1"
        self.headers = {
            "Authorization": f"SSWS {token}",
            "Accept": "application/json",
        }

    def _get_paginated(self, url: str, params: dict | None = None) -> list[dict]:
        results: list[dict] = []
        while url:
            res = requests.get(url, headers=self.headers, params=params, timeout=10)
            res.raise_for_status()
            results.extend(res.json())
            url = res.links.get("next", {}).get("url")
            params = None  # next url already includes query params
        return results

    # ── 그룹/멤버 조회 ────────────────────────────────────────────────────────

    def find_group_by_name(self, group_name: str) -> dict | None:
        res = requests.get(
            f"{self.base}/groups",
            headers=self.headers,
            params={"q": group_name, "limit": 10},
            timeout=10,
        )
        res.raise_for_status()
        for group in res.json():
            if group["profile"]["name"].lower() == group_name.lower():
                return group
        return None

    def get_group_members(self, group_id: str) -> list[dict]:
        return self._get_paginated(
            f"{self.base}/groups/{group_id}/users", params={"limit": 200}
        )

    def get_group_members_by_name(self, group_name: str) -> list[dict]:
        group = self.find_group_by_name(group_name)
        if not group:
            raise ValueError(f"그룹을 찾을 수 없습니다: {group_name}")
        return self.get_group_members(group["id"])

    def remove_user_from_group(self, group_id: str, user_id: str) -> None:
        res = requests.delete(
            f"{self.base}/groups/{group_id}/users/{user_id}",
            headers=self.headers,
            timeout=10,
        )
        if res.status_code != 204:
            res.raise_for_status()

    # ── 앱 할당 현황 조회 ─────────────────────────────────────────────────────

    def get_app_users(self, app_id: str) -> list[dict]:
        """특정 앱(SSO)에 할당된 사용자 목록을 조회합니다."""
        return self._get_paginated(
            f"{self.base}/apps/{app_id}/users", params={"limit": 500}
        )

    def find_app_by_label(self, label: str) -> dict | None:
        res = requests.get(
            f"{self.base}/apps",
            headers=self.headers,
            params={"q": label, "limit": 10},
            timeout=10,
        )
        res.raise_for_status()
        for app in res.json():
            if app.get("label") == label:
                return app
        return None

    def get_app_users_by_label(self, label: str) -> list[dict]:
        app = self.find_app_by_label(label)
        if not app:
            raise ValueError(f"앱을 찾을 수 없습니다: {label}")
        return self.get_app_users(app["id"])

    # ── 사용자 단건 조회 ──────────────────────────────────────────────────────

    def get_user(self, email_or_id: str) -> dict | None:
        res = requests.get(f"{self.base}/users/{email_or_id}", headers=self.headers, timeout=10)
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()
