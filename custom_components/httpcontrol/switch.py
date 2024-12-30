from dataclasses import dataclass
from typing import Callable, Any
from collections.abc import Mapping

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HttpcontrolCoordinator
from .entity import HttpcontrolEntity

@dataclass(frozen=True, kw_only=True)
class HttpcontrolSwitchDescription(SwitchEntityDescription):
    entity_registry_enabled_default: bool = True

SWITCHES = [
    *[
        HttpcontrolSwitchDescription(
            key=f"out{i}",
            name=f"OUT{i}",
            device_class=SwitchDeviceClass.SWITCH,
        )
        for i in range(0, 6)
    ],
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HttpcontrolCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HttpcontrolSwitch(coordinator, entity)
        for entity in SWITCHES
        if entity.key in coordinator.data.state
    )

    if coordinator.is_2x() and "out6" in coordinator.data.state:
        async_add_entities([Httpcontrol2xInvertSwitch(coordinator)])

class HttpcontrolSwitch(HttpcontrolEntity, SwitchEntity):
    entity_description: HttpcontrolSwitchDescription

    def __init__(self, coordinator: HttpcontrolCoordinator, description: HttpcontrolSwitchDescription):
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = coordinator.unique_id(description.key)
        if name := coordinator.labels.get(description.key):
            self._attr_name = name

    @property
    def is_on(self) -> bool:
        value = bool(int(self.coordinator.data.state[self.entity_description.key]))
        if self._invert():
            value = not value
        return value

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        attrs = {}
        if rtime := self.coordinator.rtimes.get(self.entity_description.key, None):
            attrs["Reset time"] = rtime
        return attrs

    async def async_turn_on(self) -> None:
        value = 0 if self._invert() else 1
        await self.coordinator.async_set_out(self.entity_description.key, value)

    async def async_turn_off(self) -> None:
        value = 1 if self._invert() else 0
        await self.coordinator.async_set_out(self.entity_description.key, value)

    def _invert(self) -> bool:
        return self.coordinator.is_2x() and bool(int(self.coordinator.data.state.get("out6", 0)))

class Httpcontrol2xInvertSwitch(HttpcontrolSwitch):
    def __init__(self, coordinator: HttpcontrolCoordinator):
        description = HttpcontrolSwitchDescription(
            key="out6",
            name="Reverse out state",
            entity_category=EntityCategory.CONFIG,
        )
        super().__init__(coordinator, description)

    @property
    def is_on(self) -> bool:
        return not bool(int(self.coordinator.data.state["out6"]))

    async def async_turn_on(self) -> None:
        self.coordinator.data.state["out6"] = "0"
        await self.coordinator.async_set_out("out", 6)

    async def async_turn_off(self) -> None:
        self.coordinator.data.state["out6"] = "1"
        await self.coordinator.async_set_out("out", 7)
