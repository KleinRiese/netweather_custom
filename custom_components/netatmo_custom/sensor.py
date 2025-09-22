from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import NetatmoDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: NetatmoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Dynamisch alle Keys als Sensoren anlegen
    # Initiale Daten sind nach first_refresh vorhanden
    entities = []
    for key in coordinator.data.keys():
        if not key:
            continue
        entities.append(NetatmoGenericSensor(coordinator, entry.entry_id, key))
    async_add_entities(entities)

class NetatmoGenericSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: NetatmoDataUpdateCoordinator, entry_id: str, key: str):
        super().__init__(coordinator)
        self._key = key
        slug = key.replace(" ", "_").replace("/", "_").replace(".", "_")
        self._attr_unique_id = f"{entry_id}_{slug}"
        self._attr_name = key

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

    def _handle_coordinator_update(self):
        # Falls neue Keys entstehen, wäre ein Reload nötig; hier nur Wertupdate
        self.async_write_ha_state()
