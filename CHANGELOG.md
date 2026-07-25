# Changelog

All notable changes to this fork are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-07-25

### Added
- **`brand/icon.png`** — restored a local brand asset so the integration
  card in Settings → Devices & Services shows the Anthbot icon while the
  official submission to `home-assistant/brands` is pending. Previously
  the icon disappeared after an update because this asset was missing
  from the repo.

---

## [1.0.2] - 2026-07-25

### Fixed
- **`Shadow request failed (429): TOO_MANY_REQUESTS`.** With the previous
  30-second polling interval, each cycle made 2 shadow requests
  (property + service) plus an occasional area-definition request. That
  translated to ~240 requests/hour, well above the Anthbot cloud rate
  limit for an idle mower. When the mower sat on the dock with no task,
  the rate limit kicked in and all entities went unavailable within a
  few minutes.
- **GPS coordinates now work.** `device_tracker.*_location` populates
  with live GPS while the mower is active. Previously the property
  shadow's `posegps` field reported `0,0` because the app opened a
  separate stream for GPS data — this release reads that stream
  correctly so the tracker updates in real time. `pose_x` / `pose_y`
  (RTK-based cartesian position) continue to work as before.

### Changed
- **Default polling interval bumped from 30s to 60s.** Existing installs
  keep their configured interval; only fresh setups use the new default.
- **Service shadow now polled every 5th cycle** instead of every cycle.
  Voice volume and similar settings still update within ~5 minutes but
  we cut request rate roughly in half. Cached last-known state is served
  between polls so no entity flips unavailable.
- **Coordinator tolerates up to 5 consecutive 429 responses** while
  keeping the previously fetched data visible to users. Only after 5
  straight rate-limit hits do entities go unavailable. First occurrence
  logs a warning; persistent failures escalate to error.

---

## [1.0.1] - 2026-05-08

### Fixed
- **403 Forbidden on shadow GET / command publish.** Anthbot rotated the
  static AWS IoT keys that the integration had been using, so all polling
  requests started failing with `403 Forbidden`. The cloud API has always
  exposed an STS endpoint that returns short-lived credentials per device
  (`access_key_id` + `secret_access_key` + `session_token`), but the
  shadow client was ignoring them and using the hardcoded keys. This
  release switches signing entirely to the dynamic STS credentials and
  adds the `x-amz-security-token` header on every signed request, with
  automatic refresh on expiration and on 403 responses.

### Added
- HACS migration guide for users coming from v0.8.x of this fork (the
  domain rename caused a "manifest.json not found" error on update).

### Changed
- README and CHANGELOG note the same migration path so it's discoverable
  from both the GitHub repo and HACS release notes.

---

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
