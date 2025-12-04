# Sector Lite

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![GitHub release](https://img.shields.io/github/v/release/marcuscasserfelt/sector-lite)](https://github.com/marcuscasserfelt/sector-lite/releases)
[![GitHub issues](https://img.shields.io/github/issues/marcuscasserfelt/sector-lite)](https://github.com/marcuscasserfelt/sector-lite/issues)
[![License](https://img.shields.io/github/license/marcuscasserfelt/sector-lite)](LICENSE)

Sector Lite is a custom Home Assistant integration for retrieving and monitoring
the alarm status of your Sector Alarm system.  
It provides a read-only `alarm_control_panel` entity and fires an event whenever
the alarm status changes, allowing powerful automations.

---

## Features

- Authenticate with your existing Sector Alarm credentials  
- Automatically selects your default panel (or first available panel)
- Displays alarm state as a Home Assistant `alarm_control_panel` entity
- Fires a Home Assistant event on status changes:
  - Event type: **`sector_lite_alarm_status_changed`**
  - Includes both previous and current states (numeric + text)
- Lightweight design intended for monitoring only

> Note: This integration **cannot arm or disarm** the alarm system.  
> It is strictly a monitoring integration.

---

## Installation

### 🟦 Install via HACS (recommended)

1. Open **HACS → Integrations**
2. Click the **⋯** menu → **Custom repositories**
3. Add:


Category: **Integration**

4. Find **Sector Lite** in the HACS list and install it
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration**
7. Search for **Sector Lite**
8. Enter your Sector Alarm **User ID** and **Password**

The integration will:

- Log in to your Sector Alarm account  
- Retrieve the list of alarm panels  
- Select the default panel (or first one found)  
- Start polling for status changes (every 30 seconds by default)

---

## Entity

The integration creates:

### `alarm_control_panel.<panel_name_sanitized>`

Attributes include:

| Attribute        | Description                           |
|------------------|---------------------------------------|
| `status`         | Numeric status from API (1/2/3)       |
| `status_text`    | `disarmed`, `armed_home`, `armed_away` |
| `panel_id`       | Sector Alarm panel ID                 |
| `panel_name`     | Display name from the Sector API      |

Current supported states:

| Sector Value | Meaning       |
|--------------|---------------|
| 1            | Disarmed      |
| 2            | Armed Home    |
| 3            | Armed Away    |

---

## Event: `sector_lite_alarm_status_changed`

Whenever the alarm state changes, the integration fires a Home Assistant event:

### Event structure

```json
{
"entry_id": "abc123",
"panel_id": "123456",
"panel_name": "My Home",
"status": 2,
"status_text": "armed_home",
"previous_status": 1,
"previous_status_text": "disarmed"
}
