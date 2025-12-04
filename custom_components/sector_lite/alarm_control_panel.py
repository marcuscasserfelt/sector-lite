"""Alarm control panel entity for Sector Lite."""

from __future__ import annotations

from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_DISARMED, STATUS_ARMED_HOME, STATUS_ARMED_AWAY
from .coordinator import SectorLiteCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sector Lite alarm control panel entity."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SectorLiteCoordinator = data["coordinator"]

    async_add_entities(
        [
            SectorLiteAlarmEntity(
                coordinator=coordinator,
                entry_id=entry.entry_id,
            )
        ]
    )


class SectorLiteAlarmEntity(CoordinatorEntity[SectorLiteCoordinator], AlarmControlPanelEntity):
    """Representation of the Sector alarm as an alarm_control_panel entity."""

    _attr_has_entity_name = True
    _attr_name = "Alarm"
    _attr_icon = "mdi:shield-home"
    _attr_supported_features = AlarmControlPanelEntityFeature(0)

    def __init__(self, coordinator: SectorLiteCoordinator, entry_id: str) -> None:
        """Initialize the alarm entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_alarm"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.panel_id)},
            "name": coordinator.panel_name,
            "manufacturer": "Sector Alarm",
            "model": "Panel",
        }

    @property
    def state(self) -> str | None:
        """Return the state of the alarm."""
        data = self.coordinator.data or {}
        status: int | None = data.get("status")
        if status == STATUS_DISARMED:
            return "disarmed"
        if status == STATUS_ARMED_HOME:
            return "armed_home"
        if status == STATUS_ARMED_AWAY:
            return "armed_away"
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        data = self.coordinator.data or {}
        return {
            "raw_status": data.get("status"),
            "status_text": data.get("status_text"),
            "panel_id": self.coordinator.panel_id,
            "panel_name": self.coordinator.panel_name,
        }
