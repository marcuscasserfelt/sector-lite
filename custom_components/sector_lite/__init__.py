"""The Sector Lite integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SectorLiteApi
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PANEL_ID,
    CONF_PANEL_NAME,
    CONF_USER_ID,
)
from .coordinator import SectorLiteCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["alarm_control_panel"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sector Lite from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username: str = entry.data[CONF_USERNAME]
    password: str = entry.data[CONF_PASSWORD]
    panel_id: str = entry.data[CONF_PANEL_ID]
    panel_name: str = entry.data[CONF_PANEL_NAME]
    user_id: str | None = entry.data.get(CONF_USER_ID)

    session = async_get_clientsession(hass)
    api = SectorLiteApi(session, username, password)

    await api.async_login()

    if not user_id and api.user_id:
        data = dict(entry.data)
        data[CONF_USER_ID] = api.user_id
        hass.config_entries.async_update_entry(entry, data=data)

    coordinator = SectorLiteCoordinator(
        hass=hass,
        api=api,
        panel_id=panel_id,
        panel_name=panel_name,
        entry_id=entry.entry_id,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
