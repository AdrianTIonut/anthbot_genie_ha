"""Data coordinator for Anthbot Genie."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AnthbotBoundDevice,
    AnthbotCloudApiClient,
    AnthbotGenieApiError,
    AnthbotShadowApiClient,
)
from .const import DOMAIN

# How many consecutive 429s to tolerate before giving up and letting entities
# go unavailable. Each poll is 60s by default, so 5 = 5 minutes of grace.
_RATE_LIMIT_SOFT_LIMIT = 5

# Poll the service shadow only once every N property polls.
# service state changes rarely (voice volume, some settings) so this
# cuts the request rate roughly in half without visible impact.
_SERVICE_SHADOW_EVERY_N = 5


class AnthbotGenieDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch and cache Anthbot shadow state."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        account_client: AnthbotCloudApiClient,
        client: AnthbotShadowApiClient,
        device: AnthbotBoundDevice,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.account_client = account_client
        self.client = client
        self.device = device
        self._area_definition: dict[str, Any] = {}
        self._last_area_time: str | None = None
        # Cache the last successful service state so we can serve it between
        # actual service-shadow polls (which we do only every N property polls).
        self._last_service_state: dict[str, Any] = {}
        # Poll counter used to decide when to fetch the service shadow.
        self._poll_counter: int = 0
        # Track consecutive 429 responses so we can serve stale data without
        # marking entities unavailable during transient cloud rate limits.
        self._consecutive_rate_limits: int = 0

    @property
    def reported_state(self) -> dict[str, Any]:
        """Return the latest reported state."""
        return self.data if isinstance(self.data, dict) else {}

    def _is_rate_limit(self, err: AnthbotGenieApiError) -> bool:
        """Return True if the API error is an HTTP 429 rate limit."""
        message = str(err)
        return "429" in message or "TOO_MANY_REQUESTS" in message

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest state from the cloud endpoint."""
        self._poll_counter += 1
        try:
            property_state = await self.client.async_get_shadow_reported_state()
        except AnthbotGenieApiError as err:
            if self._is_rate_limit(err):
                self._consecutive_rate_limits += 1
                if (
                    self._consecutive_rate_limits <= _RATE_LIMIT_SOFT_LIMIT
                    and self.data is not None
                ):
                    self.logger.warning(
                        "Anthbot cloud rate-limited us (429) [%d/%d]; "
                        "keeping previous data, will retry next poll",
                        self._consecutive_rate_limits,
                        _RATE_LIMIT_SOFT_LIMIT,
                    )
                    return self.data
                self.logger.error(
                    "Anthbot cloud rate limit persists (%d consecutive 429s); "
                    "entities will be marked unavailable until it clears",
                    self._consecutive_rate_limits,
                )
            raise UpdateFailed(str(err)) from err

        # property_state succeeded — reset the rate-limit counter.
        self._consecutive_rate_limits = 0

        # Poll service shadow only every N cycles to reduce request rate.
        # In between, keep serving the last known service state so entities
        # that depend on it (e.g. voice volume) do not flip to unavailable.
        if self._poll_counter % _SERVICE_SHADOW_EVERY_N == 1:
            try:
                self._last_service_state = (
                    await self.client.async_get_service_reported_state()
                )
            except AnthbotGenieApiError as err:
                # Non-fatal — keep the last known service state.
                self.logger.debug(
                    "Service shadow poll skipped due to error: %s", err
                )
        service_state = self._last_service_state

        area_time = property_state.get("area_time")
        if not isinstance(area_time, str):
            area_time = None
        should_refresh_area = not self._area_definition or (
            area_time is not None and area_time != self._last_area_time
        )
        if should_refresh_area:
            try:
                self._area_definition = (
                    await self.account_client.async_get_device_area_definition(
                        self.client.serial_number
                    )
                )
                self._last_area_time = area_time
            except AnthbotGenieApiError:
                if not self._area_definition:
                    self._area_definition = {}

        merged_state = dict(property_state)
        merged_state["_service_reported"] = service_state
        merged_state["_area_definition"] = self._area_definition
        return merged_state
