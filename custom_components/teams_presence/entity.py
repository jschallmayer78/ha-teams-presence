"""Base entity for Microsoft Teams Presence."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TeamsPresenceCoordinator


class TeamsPresenceEntity(CoordinatorEntity[TeamsPresenceCoordinator]):
    """Common base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TeamsPresenceCoordinator, key: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.unique_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=f"Teams {entry.title}",
            manufacturer="Microsoft",
            model="Teams Presence",
            entry_type=DeviceEntryType.SERVICE,
        )
