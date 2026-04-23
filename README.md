# Anthbot Genie Home Assistant Integration — AdrianTIonut fork

![Anthbot Genie logo](logo.png)

> **This is a community fork** of
> [vincentjanv/anthbot_genie_ha](https://github.com/vincentjanv/anthbot_genie_ha).
> All credit for the original integration — the config flow, the AWS IoT shadow
> polling with SigV4 signing, the zone handling, and the entire entity
> architecture — goes to [@vincentjanv](https://github.com/vincentjanv).
>
> This fork exists to expose additional fields from the cloud shadow that the
> upstream integration already polls but does not surface as entities. The
> domain is unchanged (`anthbot_genie`), so this is a drop-in replacement —
> existing configs keep working.

## Disclaimer

This is an unofficial, community project and is not affiliated with, endorsed
by, sponsored by, or approved by Anthbot.

All product names, logos, and trademarks are property of their respective
owners. See [NOTICE.md](NOTICE.md).

## Upstream limitations resolved in this fork

Relative to [vincentjanv/anthbot_genie_ha v0.8.0](https://github.com/vincentjanv/anthbot_genie_ha):

- [x] **GPS position on map** — upstream polled the shadow but never exposed
  `gps_latitude` / `gps_longitude` as entities. This fork adds a
  `device_tracker` platform so the mower appears on the HA map with zone
  geofencing support.
- [x] **~58 shadow fields fetched but not exposed as entities** — upstream's
  coordinator receives the full `state.reported` payload but only surfaces
  ~15 fields. This fork adds ~35 sensors and ~23 binary sensors for the
  remaining fields (firmware/board versions, OTA state, error codes,
  component life counters, RTK base state, WiFi/cellular state, camera
  state, map metadata, mowing mode flags, etc.).
- [x] **Raw numeric model id shown in device info** — upstream displayed the
  `category_id` as-is. This fork maps it through a catalog to show
  human-readable names (e.g. `Anthbot Genie 600`).
- [x] **Brands assets prepared but never submitted** — upstream's README
  noted assets were prepared for a `home-assistant/brands` PR but the PR
  was never filed, so the integration tile shows a placeholder. This fork
  ships the four correctly-sized PNGs (256 / 512 px) at
  `brands/custom_integrations/anthbot_genie/` and will submit the brands
  PR so the tile gets a real icon in Home Assistant core.

## What this fork adds on top

- **Device tracker** (`device_tracker.<device>_location`) — places the mower on
  the Home Assistant map using `gps_latitude` / `gps_longitude` from the
  shadow. Exposes RTK fix quality, heading, and satellite count as attributes.
- **~35 new sensors** — firmware/board versions, OTA state + progress + ETA,
  error code + description, event code, component life counters (cutting
  component, cutting line, recharge contact), map metadata (last-updated, total
  area, map status), RTK base state + firmware, SIM CCID, WiFi SSID, voice
  language, IP address, system boot time, anti-loss radius, custom mowing
  direction readback, appointments, and more.
- **~23 new binary sensors** — WiFi/cellular connectivity, camera state +
  error, bluetooth, accelerometer, edge-cut, obstacle-avoidance, DRC, indoor
  mode, map availability, mowing type (border vs. nest vs. full-yard), RTK
  moving, factory-reset-pending, unbind-pending, error-active, auto-upgrade,
  log upload, SIM present, anti-loss.
- **Friendly model names** via a `MODEL_NAME_BY_CATEGORY` lookup.

Upstream's sensors, switches, buttons, and services are preserved unchanged.

## What this fork does NOT change

- `domain: "anthbot_genie"` — existing users who migrate keep their
  entity history and automations.
- `codeowners` — credit preserved for the upstream author.
- The config flow, SigV4 signing, zone handling, and service layer are
  untouched.

## Architecture

This integration has been tested with an Anthbot Genie 600, but most
sensors/properties should work on other robots as well. It auto-discovers all
account-bound mowers via:

- `GET https://api.anthbot.com/api/v1/device/bind/list`

For each mower, it auto-fetches its cloud region/IoT endpoint via:

- `GET https://api.anthbot.com/api/v1/device/v2/region?sn=<sn>`

Then it polls the AWS IoT device shadow endpoint per discovered `sn` using
automatic SigV4 signing:

- `GET https://<iot_endpoint>/things/<sn>/shadow?name=property`

It also fetches the mower area definition file from Anthbot cloud to
discover manual zones and auto-zones.

## Entities

### Upstream (unchanged)

Sensors: `battery_level`, `mower_status`, `cutting_height`, `voice_volume`,
`mowing_time`, `mowing_area`, `custom_mowing_direction`,
`custom_mowing_direction_enabled`, `zones`, `auto_zones`.

Binary sensors: `connection`, `charging`.

Switches: `custom_mowing_direction_enabled`, `rain_perception_enabled`.

Number controls: `mow_height`, `voice_volume`, `custom_mowing_direction`,
`rain_continue_time`.

Buttons: `Start full mow`, `Stop mow`, `Return to dock`, `Zone <name>`
(per manual zone), `Auto zone <name>` (per auto-zone).

### Added by this fork

Sensors (selection):

- `firmware_version`, `main_board_version`, `extension_board_version`,
  `rtk_base_firmware`, `protocol_version`, `minimum_app_version`
- `ota_state`, `ota_progress`, `ota_time_estimate`
- `error_code`, `error_description`, `event_code`
- `gps_latitude`, `gps_longitude`, `rtk_state`, `rtk_base_state`
- `cutting_component_life`, `cutting_line_life`, `recharge_contact_life`
- `map_status`, `total_map_area`, `map_last_updated`, `path_last_updated`,
  `area_last_updated`
- `wifi_ssid`, `ip_address`, `sim_ccid`, `voice_language`, `pin_code`,
  `mow_count`, `next_appointment`, `anti_loss_radius`,
  `obstacle_avoidance_level`, `system_boot_time`, `shadow_updated`

Binary sensors (selection):

- `wifi_connected`, `cellular_connected`, `cellular_heartbeat`,
  `bluetooth_active`, `accelerometer_active`, `sim_present`
- `camera_state`, `camera_error`, `edge_cut_state`,
  `obstacle_avoidance_state`, `rtk_moving`
- `mowing_border`, `mowing_nest`, `full_yard_mowing`
- `map_available`, `drc_enabled`, `indoor_mode_state`, `log_upload_enabled`
- `auto_upgrade_state`, `factory_reset_pending`, `unbind_pending`,
  `error_active`, `anti_loss_state`

Device tracker: `<device>_location`.

## Setup

### HACS (custom repository)

1. Open HACS → Integrations → top-right menu → `Custom repositories`.
2. Add repository URL: `https://github.com/AdrianTIonut/anthbot_genie_ha`
3. Category: `Integration`
4. Install `Anthbot Genie` from HACS and restart Home Assistant.
5. Add integration: `Settings → Devices & Services → Add Integration →
   Anthbot Genie`.

### Manual

1. Copy `custom_components/anthbot_genie` into your Home Assistant config
   directory.
2. Restart Home Assistant.
3. Add integration: `Settings → Devices & Services → Add Integration →
   Anthbot Genie`.
4. In config, enter Anthbot `username` / `password`, select your country
   (area code dropdown).
5. The rest (device discovery, region, IoT endpoint, shadow auth signing)
   is automatic.

## Home Assistant Brands (integration tile icon)

To show the icon in Home Assistant's integration tile, a PR must be
submitted to `home-assistant/brands`. Prepared assets are included at
`brands/custom_integrations/anthbot_genie/` — `icon.png`, `icon@2x.png`,
`logo.png`, `logo@2x.png` — pre-sized to the required 256 / 512 px.

## Actions (services)

The integration provides these Home Assistant services (unchanged from
upstream):

- `anthbot_genie.start_full_mow`
- `anthbot_genie.stop_mow`
- `anthbot_genie.return_to_dock`
- `anthbot_genie.set_mow_height` (`mow_height`: 30..70 in 5 mm steps)
- `anthbot_genie.set_voice_volume` (`voice_volume`: 0..100)
- `anthbot_genie.set_custom_mowing_direction` (`mow_direction`: 0..180,
  `enable_custom_direction`: true/false)
- `anthbot_genie.start_zone_mow` (`zones`: id, name, comma-separated string,
  or YAML list)
- `anthbot_genie.start_auto_zone_mow` (`auto_zones`: id, name,
  comma-separated string, or YAML list)

Target by entity (`target.entity_id`) and/or by `serial_number`.

Examples:

```yaml
service: anthbot_genie.start_zone_mow
target:
  entity_id: sensor.cleaver_zones
data:
  zones: [100]
```

```yaml
service: anthbot_genie.start_auto_zone_mow
target:
  entity_id: sensor.cleaver_auto_zones
data:
  auto_zones: "1, Front area"
```

## Device page controls

The integration creates control entities on each mower device page:

- Buttons: `Start full mow`, `Stop mow`, `Return to dock`
- Buttons: one `Zone <name>` per manual zone
- Buttons: one `Auto zone <name>` per auto-zone
- Number controls: `Mow height`, `Voice volume`, `Custom mowing direction`
  (0..180), `Rain continue time` (0..8h)
- Switches: `Custom mowing direction enabled`, `Rain perception`
- Sensors: `Zones`, `Auto zones` with zone ids/names summaries

## Issues and discussions

For bugs or feature requests specific to this fork, open an issue at
[AdrianTIonut/anthbot_genie_ha/issues](https://github.com/AdrianTIonut/anthbot_genie_ha/issues).

For upstream issues (anything unrelated to this fork's additions), please
open them in the
[upstream repository](https://github.com/vincentjanv/anthbot_genie_ha/issues).

## Credits

- Original integration by [@vincentjanv](https://github.com/vincentjanv) —
  [vincentjanv/anthbot_genie_ha](https://github.com/vincentjanv/anthbot_genie_ha).
  This fork would not exist without their foundational work on the cloud
  API reverse engineering and the SigV4-signed shadow polling.
- Fork additions (extra entities, device tracker, brands assets) by
  [@AdrianTIonut](https://github.com/AdrianTIonut).
