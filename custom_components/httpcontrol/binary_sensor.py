from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HttpcontrolData, HttpcontrolCoordinator
from .entity import HttpcontrolEntity

PARALLEL_UPDATES = 0

@dataclass(frozen=True, kw_only=True)
class HttpcontrolBinarySensorDescription(BinarySensorEntityDescription):
    entity_registry_enabled_default: bool = True
    value_fn: Callable


SENSORS_2x = [
    HttpcontrolBinarySensorDescription(
        key=f"di{i}",
        name=f"INP{i}D",
        value_fn=lambda x: x == "up"
    ) for i in range(0, 4)
]
SENSORS_3x = [
    HttpcontrolBinarySensorDescription(
        key=f"ind{i}",
        name=f"INP{i}D",
        value_fn=lambda x: bool(x)
    ) for i in range(0, 4)
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HttpcontrolCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = SENSORS_3x if coordinator.is_3x() else SENSORS_2x
    async_add_entities(
        HttpcontrolBinarySensor(coordinator, entity)
        for entity in entities
        if entity.key in coordinator.data.state
    )

class HttpcontrolBinarySensor(HttpcontrolEntity, BinarySensorEntity):
    entity_description: HttpcontrolBinarySensorDescription

    def __init__(self, coordinator: HttpcontrolCoordinator, description: HttpcontrolBinarySensorDescription):
        super().__init__(coordinator, description)

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data.state[self.entity_description.key])
