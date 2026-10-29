"""Data update coordinator for Microsoft Teams Presence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GraphAuthError, GraphClient, GraphError, GraphRateLimitError, to_snake_case
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type TeamsPresenceConfigEntry = ConfigEntry[TeamsPresenceCoordinator]


@dataclass(frozen=True)
class PresenceData:
    """Parsed presence information."""

    availability: str | None
    activity: str | None
    raw_availability: str | None
    raw_activity: str | None
    status_message: str | None
    status_message_expiry: str | None
    out_of_office: bool
    out_of_office_message: str | None


class TeamsPresenceCoordinator(DataUpdateCoordinator[PresenceData]):
    """Poll /me/presence."""

    config_entry: TeamsPresenceConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: TeamsPresenceConfigEntry,
        client: GraphClient,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.client = client

    async def _async_update_data(self) -> PresenceData:
        try:
            data = await self.client.async_get_presence()
        except GraphAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except GraphRateLimitError as err:
            raise UpdateFailed(str(err), retry_after=err.retry_after) from err
        except GraphError as err:
            raise UpdateFailed(str(err)) from err

        return _parse_presence(data)


def _parse_presence(data: dict[str, Any]) -> PresenceData:
    status: dict[str, Any] = data.get("statusMessage") or {}
    message: dict[str, Any] = status.get("message") or {}
    expiry: dict[str, Any] = status.get("expiryDateTime") or {}
    ooo: dict[str, Any] = data.get("outOfOfficeSettings") or {}

    return PresenceData(
        availability=to_snake_case(data.get("availability")),
        activity=to_snake_case(data.get("activity")),
        raw_availability=data.get("availability"),
        raw_activity=data.get("activity"),
        status_message=message.get("content") or None,
        status_message_expiry=expiry.get("dateTime"),
        out_of_office=bool(ooo.get("isOutOfOffice")),
        out_of_office_message=ooo.get("message") or None,
    )
