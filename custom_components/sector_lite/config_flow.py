"""Config flow for Sector Lite."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SectorLiteApi, SectorLiteApiError, SectorLiteAuthError
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PANEL_ID,
    CONF_PANEL_NAME,
    CONF_USER_ID,
)

_LOGGER = logging.getLogger(__name__)


async def _test_connection(
    hass: HomeAssistant, username: str, password: str
) -> dict[str, Any]:
    session = async_get_clientsession(hass)
    api = SectorLiteApi(session, username, password)

    await api.async_login()
    panels = await api.async_get_panels()

    if not panels:
        raise SectorLiteApiError("No panels found")

    default_panel = next((p for p in panels if p.get("IsDefaultPanel")), None)
    panel = default_panel or panels[0]

    panel_id = panel.get("PanelId")
    panel_name = panel.get("DisplayName") or f"Panel {panel_id}"

    return {
        CONF_PANEL_ID: panel_id,
        CONF_PANEL_NAME: panel_name,
        CONF_USER_ID: api.user_id,
    }


class SectorLiteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}

        if user_input:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            try:
                result = await _test_connection(
                    self.hass, username, password
                )
            except SectorLiteAuthError:
                errors["base"] = "invalid_auth"
            except SectorLiteApiError:
                errors["base"] = "cannot_connect"
            else:
                unique_id = result.get(CONF_USER_ID) or username
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=result[CONF_PANEL_NAME],
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_PANEL_ID: result[CONF_PANEL_ID],
                        CONF_PANEL_NAME: result[CONF_PANEL_NAME],
                        CONF_USER_ID: result.get(CONF_USER_ID),
                    }
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
