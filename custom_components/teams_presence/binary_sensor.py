"""Binary sensors for Microsoft Teams Presence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CALL_ACTIVITIES
from .coordinator import PresenceData, TeamsPresenceConfigEntry, TeamsPresenceCoordinator
from .entity import TeamsPresenceEntity


@dataclass(frozen=True, kw_only=True)
class TeamsBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Teams binary sensor."""

    is_on_fn: Callable[[PresenceData], bool | None]


BINARY_SENSORS: tuple[TeamsBinarySensorEntityDescription, ...] = (
    TeamsBinarySensorEntityDescription(
        key="in_call",
        is_on_fn=lambda d: d.activity in CALL_ACTIVITIES,
    ),
    TeamsBinarySensorEntityDescription(
        key="busy",
        is_on_fn=lambda d: d.availability in {"busy", "busy_idle", "do_not_disturb"},
    ),
    TeamsBinarySensorEntityDescription(
        key="online",
        is_on_fn=lambda d: d.availability
        not in {None, "offline", "presence_unknown"},
    ),
    TeamsBinarySensorEntityDescription(
        key="out_of_office",
        is_on_fn=lambda d: d.out_of_office,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeamsPresenceConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(TeamsBinarySensor(coordinator, desc) for desc in BINARY_SENSORS)


class TeamsBinarySensor(TeamsPresenceEntity, BinarySensorEntity):
    """Teams presence binary sensor."""

    entity_description: TeamsBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: TeamsPresenceCoordinator,
        description: TeamsBinarySensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if on."""
        return self.entity_description.is_on_fn(self.coordinator.data)
