"""API client for the Sector Lite integration."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession, ClientError

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://mypagesapi.sectoralarm.net/api"


class SectorLiteApiError(Exception):
    """General API error."""


class SectorLiteAuthError(SectorLiteApiError):
    """Authentication error."""


class SectorLiteApi:
    """Async client for Sector Alarm API."""

    def __init__(self, session: ClientSession, username: str, password: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._token: Optional[str] = None
        self._user_id: Optional[str] = None

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    async def async_login(self) -> None:
        """Authenticate, store JWT and user ID."""
        url = f"{BASE_URL}/Login/Login"
        payload = {
            "userId": self._username,
            "password": self._password,
        }

        try:
            async with self._session.post(url, json=payload) as resp:
                if resp.status == 401:
                    raise SectorLiteAuthError("Invalid username or password")
                if resp.status != 200:
                    raise SectorLiteApiError(f"Unexpected status during login: {resp.status}")

                data = await resp.json()

        except ClientError as err:
            raise SectorLiteApiError(f"Communication error: {err}") from err

        token = data.get("AuthorizationToken")
        user = data.get("User") or {}
        user_id = user.get("Id")

        if not token or not user_id:
            raise SectorLiteApiError("Login response missing token or user id")

        self._token = token
        self._user_id = user_id

    def _auth_headers(self) -> Dict[str, str]:
        if not self._token:
            raise SectorLiteAuthError("Not authenticated")
        return {"Authorization": f"Bearer {self._token}"}

    async def async_get_panels(self) -> List[Dict[str, Any]]:
        url = f"{BASE_URL}/account/GetPanelList"

        try:
            async with self._session.get(url, headers=self._auth_headers()) as resp:
                if resp.status == 401:
                    raise SectorLiteAuthError("Unauthorized while fetching panels")
                if resp.status != 200:
                    raise SectorLiteApiError(f"Unexpected status: {resp.status}")

                data = await resp.json()

        except ClientError as err:
            raise SectorLiteApiError(f"Communication error: {err}") from err

        if not isinstance(data, list):
            raise SectorLiteApiError("Panel list response is not a list")

        return data

    async def async_get_panel_status(self, panel_id: str) -> Dict[str, Any]:
        url = f"{BASE_URL}/panel/GetPanelStatus"
        params = {"panelId": panel_id}

        try:
            async with self._session.get(
                url, headers=self._auth_headers(), params=params
            ) as resp:
                if resp.status == 401:
                    raise SectorLiteAuthError("Unauthorized while fetching panel status")
                if resp.status != 200:
                    raise SectorLiteApiError(f"Unexpected status: {resp.status}")

                data = await resp.json()

        except ClientError as err:
            raise SectorLiteApiError(f"Communication error: {err}") from err

        if "Status" not in data:
            raise SectorLiteApiError("Panel status missing 'Status'")

        return data
