"""Coordinator for Sector Lite."""

from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SectorLiteApi, SectorLiteApiError, SectorLiteAuthError
from .const import (
    DEFAULT_SCAN_INTERVAL,
    EVENT_ALARM_STATUS_CHANGED,
    STATUS_MAP,
)

_LOGGER = logging.getLogger(__name__)


class SectorLiteCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator handling status updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SectorLiteApi,
        panel_id: str,
        panel_name: str,
        entry_id: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"sector_lite_{panel_id}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._api = api
        self._panel_id = panel_id
        self._panel_name = panel_name
        self._entry_id = entry_id
        self._last_status: Optional[int] = None

    @property
    def panel_id(self) -> str:
        return self._panel_id

    @property
    def panel_name(self) -> str:
        return self._panel_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest panel status."""
        try:
            data = await self._api.async_get_panel_status(self._panel_id)
        except SectorLiteAuthError:
            await self._api.async_login()
            data = await self._api.async_get_panel_status(self._panel_id)
        except SectorLiteApiError as err:
            raise UpdateFailed(str(err)) from err

        status = int(data.get("Status"))
        previous = self._last_status

        if previous is not None and previous != status:
            self.hass.bus.async_fire(
                EVENT_ALARM_STATUS_CHANGED,
                {
                    "entry_id": self._entry_id,
                    "panel_id": self._panel_id,
                    "panel_name": self._panel_name,
                    "status": status,
                    "status_text": STATUS_MAP.get(status, "unknown"),
                    "previous_status": previous,
                    "previous_status_text": STATUS_MAP.get(previous, "unknown"),
                },
            )

        self._last_status = status

        return {
            "status": status,
            "status_text": STATUS_MAP.get(status, "unknown"),
        }
