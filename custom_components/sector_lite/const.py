"""Constants for the Sector Lite integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "sector_lite"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_PANEL_ID = "panel_id"
CONF_PANEL_NAME = "panel_name"
CONF_USER_ID = "user_id"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

EVENT_ALARM_STATUS_CHANGED = "sector_lite_alarm_status_changed"

STATUS_DISARMED = 1
STATUS_ARMED_HOME = 2
STATUS_ARMED_AWAY = 3

STATUS_MAP = {
    STATUS_DISARMED: "disarmed",
    STATUS_ARMED_HOME: "armed_home",
    STATUS_ARMED_AWAY: "armed_away",
}
