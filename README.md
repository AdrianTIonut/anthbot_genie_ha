# Anthbot Genie Plus — Home Assistant Integration

[![License: MIT](https://img.shields.io/github/license/AdrianTIonut/anthbot_genie_ha?color=blue)](LICENSE)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/AdrianTIonut/anthbot_genie_ha?label=latest%20release)](https://github.com/AdrianTIonut/anthbot_genie_ha/releases/latest)
[![GitHub release downloads](https://img.shields.io/github/downloads/AdrianTIonut/anthbot_genie_ha/total?label=downloads)](https://github.com/AdrianTIonut/anthbot_genie_ha/releases)
[![GitHub stars](https://img.shields.io/github/stars/AdrianTIonut/anthbot_genie_ha?label=stars&color=yellow)](https://github.com/AdrianTIonut/anthbot_genie_ha/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/AdrianTIonut/anthbot_genie_ha?label=forks&color=orange)](https://github.com/AdrianTIonut/anthbot_genie_ha/network/members)
[![GitHub issues](https://img.shields.io/github/issues/AdrianTIonut/anthbot_genie_ha?label=open%20issues)](https://github.com/AdrianTIonut/anthbot_genie_ha/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/AdrianTIonut/anthbot_genie_ha?label=open%20PRs)](https://github.com/AdrianTIonut/anthbot_genie_ha/pulls)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

![Anthbot Genie logo](logo.png)

A Home Assistant custom integration for **Anthbot Genie** robotic lawn
mowers, with extended sensors, services, and zone control beyond the
upstream integration.

> **Independent fork.** Domain `anthbot_genie_plus` — installs alongside
> the upstream [vincentjanv/anthbot_genie_ha](https://github.com/vincentjanv/anthbot_genie_ha)
> without conflict, so you can have both running side-by-side or migrate.
> All credit for the original architecture (config flow, AWS IoT SigV4
> signing, shadow polling, zone resolver) goes to
> [@vincentjanv](https://github.com/vincentjanv).

---

## ✨ What this fork adds

Compared to upstream `vincentjanv/anthbot_genie_ha v0.8.0`:

- **78+ entities** from the cloud shadow (see full list below)
- **Maintenance % sensors** — blade wear, cutting line, rotor (the
  `robot_maintenance` fields nobody else exposes)
- **Live position sensors** (`pose_x`, `pose_y`, `pose_yaw`) — robot's
  absolute cartesian position on the map; updates in real time
  while mowing
- **Active zone sensor** + **no-go zones counter**
- **`robot_sta` attribute** on `binary_sensor.*_connection` — exposes
  the cloud's robot status string (`globalmowing`, `charge`, `idle`,
  etc.) directly for use in automations
- **Service** `start_zone_mow` for per-zone mowing (with name or ID)
- **Services** `start_full_mow`, `stop_mow`, `return_to_dock`
- **Services** `set_custom_mowing_direction`, `set_mow_height`,
  `set_voice_volume`
- **Brand assets** registered for HA's device picker
- **Per-mower entity prefix** so multiple mowers in one account stay
  cleanly separated

> **GPS location — working (since v1.0.2)**: `device_tracker.*_location`
> now populates with live GPS coordinates while the mower is active. The
> `pose_x` / `pose_y` sensors remain available for absolute cartesian
> position on the map (updated via RTK).

---

## 📋 Full entity list

### 🔵 Sensors (~44)

**Battery & Power**
- `battery_level` — % charge

**Mower Status**
- `mower_status` — current state (mowing / charging / idle / paused / etc.)
- `error_code`, `error_description` — failures
- `event_code` — last firmware event
- `system_boot_time` — last boot
- `shadow_updated` — last cloud-sync time

**Maintenance** (the wear % values from `robot_maintenance`)
- `cutting_components_life` — blade wear remaining
- `cutting_line_life` — cutting line remaining
- `recharge_contact_life` — charging contact wear

**Mowing Stats**
- `mowing_time`, `mowing_area` — current/last session
- `cutting_height` — current setting
- `custom_mowing_direction`, `custom_mowing_direction_enabled`
- `mow_count` — passes per session
- `obstacle_avoidance_level` — POB control level

**Map & Zones**
- `total_map_area` — m² total mapped
- `map_status` — idle / mapping / mapping_pause
- `zones`, `auto_zones` — per-zone definitions (with names, vertices)
- `area_last_updated`, `map_last_updated`, `path_last_updated`

**Position**
- `gps_latitude`, `gps_longitude`

**RTK / Navigation**
- `rtk_state`, `rtk_base_state`, `rtk_base_firmware`

**Network & Hardware IDs**
- `ip_address`, `wifi_ssid`
- `sim_ccid` — SIM card ID
- `pin_code` — Genie PIN
- `voice_volume`, `voice_language`
- `anti_loss_radius` — anti-theft tether radius

**Firmware Versions**
- `firmware_version` — system version
- `main_board_version`, `extension_board_version`
- `protocol_version`, `minimum_app_version`

**OTA / Updates**
- `ota_progress`, `ota_state`, `ota_time_estimate`

**Schedules**
- `next_appointment` — next scheduled task

### 🟢 Binary Sensors (~25)

- `connection`, `charging`
- `cellular_connected`, `cellular_heartbeat`, `sim_present`
- `wifi_connected`, `bluetooth_active`
- `camera_state`, `camera_error`
- `accelerometer_active`
- `anti_loss_state` — anti-theft active
- `auto_upgrade_state`
- `drc_enabled`, `edge_cut_state`, `indoor_mode_state`
- `error_active`
- `factory_reset_pending`, `unbind_pending`
- `full_yard_mowing` — full mow flag
- `log_upload_enabled`
- `map_available`
- `mowing_border`, `mowing_nest`
- `obstacle_avoidance_state`
- `rtk_moving`

### 🎛️ Controls

**Numbers (sliders)**
- `mow_height_setting` — 30-70 mm
- `voice_volume_setting` — 0-100%
- `custom_mowing_direction_setting` — 0-180°
- `rain_continue_time_setting` — 0-8 hours

**Switches**
- `custom_mowing_direction_enabled` — apply custom direction or default
- `rain_perception_enabled` — built-in rain sensor on/off

**Buttons**
- `start_full_mow`, `stop_mow`, `return_to_dock`

**Device Tracker**
- Live GPS location on map

### 🛠️ Services

- `anthbot_genie_plus.start_full_mow` — full lawn
- `anthbot_genie_plus.start_zone_mow` — by zone name or ID
- `anthbot_genie_plus.start_auto_zone_mow` — auto-detected zones
- `anthbot_genie_plus.stop_mow`
- `anthbot_genie_plus.return_to_dock`
- `anthbot_genie_plus.set_mow_height`
- `anthbot_genie_plus.set_voice_volume`
- `anthbot_genie_plus.set_custom_mowing_direction`

---

## 📦 Installation

### Via HACS (recommended)

1. Open HACS → Integrations
2. Three dots top right → **Custom repositories**
3. Repository: `https://github.com/AdrianTIonut/anthbot_genie_ha`
4. Type: **Integration**
5. Click **Add**
6. Search for "**Anthbot Genie Plus**" in HACS → Install
7. Restart Home Assistant
8. Settings → Devices & Services → **Add Integration** → "Anthbot Genie Plus"
9. Enter your Anthbot account email + password

### Manual

1. Copy `custom_components/anthbot_genie_plus/` to your HA's
   `/config/custom_components/anthbot_genie_plus/`
2. Restart HA
3. Add via UI like above

---

## 🔄 Migrating from upstream `anthbot_genie`

If you already have `vincentjanv/anthbot_genie_ha` installed:

1. **Backup**: note any automations / dashboards that reference
   `sensor.anthbot_*` entity_ids
2. Install this fork via HACS as above. Domain is different
   (`anthbot_genie_plus`), so they coexist for now.
3. Add the integration in HA UI → entities appear with prefix
   `anthbot_genie_plus_` (or similar slug, depending on device naming)
4. Update your automations / dashboards to the new entity_ids
5. Once everything works, optionally remove the upstream integration
   to avoid duplicated data

---

## ⚠️ Updating from this fork's v0.8.x to v1.0.0

In v1.0.0 the domain was renamed `anthbot_genie` → `anthbot_genie_plus`,
so the integration folder also moved from
`custom_components/anthbot_genie/` to
`custom_components/anthbot_genie_plus/`.

HACS caches the original folder path per repository, so when it tries to
download v1.0.0 it may look for the **old** path and fail with:

```
Downloading AdrianTIonut/anthbot_genie_ha with version v1.0.0 failed with
(No manifest.json file found 'custom_components/anthbot_genie/manifest.json')
```

To fix, force HACS to re-read the new folder layout:

1. HACS → **Anthbot Genie** (the old entry) → ⋮ → **Remove**
2. Restart Home Assistant
3. HACS → **Custom repositories** → re-add
   `https://github.com/AdrianTIonut/anthbot_genie_ha` as **Integration**
4. Open the new entry → **Download** → pick v1.0.0
5. Restart Home Assistant
6. Settings → Devices & Services → the old `Anthbot Genie` integration
   will show **Failed setup** (folder no longer exists) — remove it.
7. **Add Integration** → search **Anthbot Genie Plus** → log in with the
   same Anthbot account (no need to re-enter credentials elsewhere).

Your existing dashboards / automations using the old `sensor.anthbot_*`
entity_ids must be updated to `sensor.anthbot_genie_plus_*` (the device
slug may be different too — check Developer Tools → States).

---

## ⚙️ Configuration

You only need:
- **Anthbot account email** (the one you use in the mobile app)
- **Password**
- **Country** (auto-detected; manual override available)
- **Polling interval** (default 30s)

Multi-mower accounts are supported — each device gets its own entity
prefix.

---

## 🚫 Disclaimer

Unofficial, community project. Not affiliated with, endorsed by, or
sponsored by **Anthbot**. All product names, logos, and trademarks are
property of their respective owners. See [NOTICE.md](NOTICE.md) for
attribution to the upstream project and trademark notes.

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE)
for details. Original upstream code is also MIT-licensed.

---

## 🐛 Issues / Feature requests

Open an issue at:
[github.com/AdrianTIonut/anthbot_genie_ha/issues](https://github.com/AdrianTIonut/anthbot_genie_ha/issues)

Please **do not include** sensitive information in issues:
- Serial numbers
- PIN codes
- Email / password
- GPS coordinates of your home

If a log or stack trace is needed for debugging, redact those fields
before pasting. Issues with sensitive data will be edited to remove it.

---

## 🤝 Contributing

PRs welcome — keep changes focused and add a CHANGELOG entry. The
upstream integration's architecture (one coordinator per mower, AWS IoT
shadow polling) is non-trivial; preserve it where possible.
