# Changelog

All notable changes to this fork are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-01

First independent release of the fork. Domain renamed to
`anthbot_genie_plus` so it can be installed alongside the upstream
[vincentjanv/anthbot_genie_ha](https://github.com/vincentjanv/anthbot_genie_ha)
without conflict.

### Added
- **Domain**: `anthbot_genie_plus` (separate from upstream's `anthbot_genie`)
- **Friendly name**: "Anthbot Genie Plus" (entities prefixed accordingly)
- **MIT LICENSE** file (matching the upstream)
- **`sensor.*_pose_x` / `_pose_y` / `_pose_yaw`** — robot's absolute
  cartesian position on the map (cm + degrees), updates in real time
  while mowing. Useful to plot Genie's path on a custom dashboard.
- **`sensor.*_active_zone`** — id of the currently-active mowing zone
  from `active_area`.
- **`sensor.*_no_go_zones`** — count of forbid zones defined on the
  device (read from `_area_definition.forbid_areas`).
- **`robot_sta` attribute** on `binary_sensor.*_connection` — exposes
  the cloud's robot status string (e.g. `globalmowing`, `charge`,
  `idle`) directly so it can be used in automations / templates.

### Changed
- README rewritten with badges (license, latest release, downloads,
  HACS), explicit attribution to the upstream project, full entity
  list, and migration guide for users coming from upstream.
- `BRANDS_SUBMISSION.md`, `hacs.json`, manifest and translations
  updated for the new domain.

### Known limitations / WIP
- **GPS location** (`device_tracker.*_location`) — Anthbot's recent
  firmware/cloud changes appear to no longer publish live GPS coords
  in the property shadow (`anti_loss_pose.posegps` reports `0,0` even
  while mowing). The entity still exists; it will populate once the
  data path is confirmed. Investigation in progress.

### Migrating from `anthbot_genie` (upstream or older fork)

The two integrations now coexist without conflicts. Procedure:

1. Update via HACS to v1.0.0 (or copy the new
   `custom_components/anthbot_genie_plus/` folder manually).
2. Restart Home Assistant.
3. Settings → Devices & Services → **Add Integration** → search
   "Anthbot Genie Plus" → log in with your Anthbot account.
4. Update any automations / dashboards from `sensor.anthbot_*` to
   `sensor.<your_mower_slug>_*` (the entity slugs are derived from
   the device alias, not the domain).
5. Once the new integration is happy, you can remove the old one
   from Devices & Services to avoid duplicate polling.

### ⚠️ HACS update from v0.8.x of this fork

If HACS shows the error
`No manifest.json file found 'custom_components/anthbot_genie/manifest.json'`
when updating to v1.0.0, it's because HACS cached the old folder path
(`anthbot_genie`) from your previous install. The folder is now
`anthbot_genie_plus`. To fix:

1. HACS → **Anthbot Genie** (old entry) → ⋮ → **Remove**.
2. Restart Home Assistant.
3. HACS → **Custom repositories** → re-add
   `https://github.com/AdrianTIonut/anthbot_genie_ha` as **Integration**.
4. Download v1.0.0, restart HA.
5. The old failed integration in Devices & Services can be removed.
6. Add **Anthbot Genie Plus** via *Add Integration* and log in.

---

## [0.8.2] - 2026-04-27

### Fixed
- `manifest.json` was missing the closing `}` brace, causing HACS to
  fail to add the repository with `unexpected end of data: line 11
  column 1`. Added the brace and tagged a fresh release so HACS
  picks up a valid manifest.

## [0.8.1] - earlier

Earlier fork work, see git history.
