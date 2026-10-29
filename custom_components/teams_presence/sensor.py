"""Sensors for Microsoft Teams Presence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ACTIVITY_STATES, AVAILABILITY_STATES
from .coordinator import PresenceData, TeamsPresenceConfigEntry, TeamsPresenceCoordinator
from .entity import TeamsPresenceEntity


@dataclass(frozen=True, kw_only=True)
class TeamsSensorEntityDescription(SensorEntityDescription):
    """Describes a Teams sensor."""

    value_fn: Callable[[PresenceData], str | None]
    attr_fn: Callable[[PresenceData], dict[str, Any]] | None = None


def _enum_value(value: str | None, options: list[str]) -> str | None:
    if value is None:
        return None
    return value if value in options else "presence_unknown"


SENSORS: tuple[TeamsSensorEntityDescription, ...] = (
    TeamsSensorEntityDescription(
        key="availability",
        device_class=SensorDeviceClass.ENUM,
        options=AVAILABILITY_STATES,
        value_fn=lambda d: _enum_value(d.availability, AVAILABILITY_STATES),
        attr_fn=lambda d: {
            "raw": d.raw_availability,
            "status_message": d.status_message,
            "out_of_office": d.out_of_office,
        },
    ),
    TeamsSensorEntityDescription(
        key="activity",
        device_class=SensorDeviceClass.ENUM,
        options=ACTIVITY_STATES,
        value_fn=lambda d: _enum_value(d.activity, ACTIVITY_STATES),
        attr_fn=lambda d: {"raw": d.raw_activity},
    ),
    TeamsSensorEntityDescription(
        key="status_message",
        value_fn=lambda d: d.status_message[:255] if d.status_message else None,
        attr_fn=lambda d: {
            "full_message": d.status_message,
            "expires": d.status_message_expiry,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeamsPresenceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data
    async_add_entities(TeamsSensor(coordinator, desc) for desc in SENSORS)


class TeamsSensor(TeamsPresenceEntity, SensorEntity):
    """Teams presence sensor."""

    entity_description: TeamsSensorEntityDescription

    def __init__(
        self,
        coordinator: TeamsPresenceCoordinator,
        description: TeamsSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes."""
        if self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)
