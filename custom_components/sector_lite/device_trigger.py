"""Device triggers for Sector Lite."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_PLATFORM,
    CONF_TYPE,
    CONF_FROM,
    CONF_TO,
)
from homeassistant.core import HomeAssistant
from homeassistant.components.automation.event import (
    async_attach_trigger as async_attach_event_trigger,
)
from homeassistant.components.device_automation import (
    DEVICE_TRIGGER_BASE_SCHEMA,
)
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, EVENT_ALARM_STATUS_CHANGED

TRIGGER_TYPE_STATUS_CHANGED = "status_changed"
TRIGGER_TYPE_DISARMED = "disarmed"
TRIGGER_TYPE_ARMED_HOME = "armed_home"
TRIGGER_TYPE_ARMED_AWAY = "armed_away"

TRIGGER_TYPES: list[str] = [
    TRIGGER_TYPE_STATUS_CHANGED,
    TRIGGER_TYPE_DISARMED,
    TRIGGER_TYPE_ARMED_HOME,
    TRIGGER_TYPE_ARMED_AWAY,
]

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)

STATUS_TEXTS = [TRIGGER_TYPE_DISARMED, TRIGGER_TYPE_ARMED_HOME, TRIGGER_TYPE_ARMED_AWAY]

CAPABILITIES_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FROM): vol.In(STATUS_TEXTS),
        vol.Optional(CONF_TO): vol.In(STATUS_TEXTS),
    }
)


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> list[dict[str, Any]]:
    """List device triggers for Sector Lite devices."""
    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get(device_id)
    if device is None:
        return []

    # Only expose triggers if this device belongs to our domain
    if not any(domain == DOMAIN for domain, _ in device.identifiers):
        return []

    return [
        {CONF_PLATFORM: "device", CONF_DOMAIN: DOMAIN, CONF_DEVICE_ID: device_id, CONF_TYPE: t}
        for t in TRIGGER_TYPES
    ]


async def async_get_trigger_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """Return the capabilities of the trigger."""
    # Only the generic status_changed trigger supports from/to filters
    if config.get(CONF_TYPE) == TRIGGER_TYPE_STATUS_CHANGED:
        return {"extra_fields": CAPABILITIES_SCHEMA}
    return {"extra_fields": vol.Schema({})}


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action,
    trigger_info,
):
    """Attach a trigger for Sector Lite device."""
    config = TRIGGER_SCHEMA(config)

    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get(config[CONF_DEVICE_ID])
    if device is None:
        # No device; never fire
        return lambda: None

    # Extract the panel_id from device identifiers: (DOMAIN, panel_id)
    panel_id: str | None = None
    for domain, ident in device.identifiers:
        if domain == DOMAIN:
            panel_id = ident
            break

    if panel_id is None:
        return lambda: None

    # Base event filter always includes the panel_id for scoping
    event_data: dict[str, Any] = {"panel_id": panel_id}

    trig_type = config[CONF_TYPE]
    if trig_type in STATUS_TEXTS:
        # Direct, e.g. armed_home/disarmed
        event_data["status_text"] = trig_type
    else:
        # status_changed with optional from/to filters
        if CONF_FROM in config:
            event_data["previous_status_text"] = config[CONF_FROM]
        if CONF_TO in config:
            event_data["status_text"] = config[CONF_TO]

    event_trigger_config: dict[str, Any] = {
        CONF_PLATFORM: "event",
        "event_type": EVENT_ALARM_STATUS_CHANGED,
        "event_data": event_data,
    }

    return await async_attach_event_trigger(
        hass, event_trigger_config, action, trigger_info
    )
