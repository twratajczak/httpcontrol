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
    device_class=SwitchDeviceClass.SWITCH,

SWITCHES_1x = [
    HttpcontrolSwitchDescription(
        key=f"out{i}",
        name=f"OUT{i}",
    ) for i in range(0, 5)
]

SWITCHES_2x = [
    HttpcontrolSwitchDescription(
        key=f"out{i}",
        name=f"OUT{i}",
    ) for i in range(0, 6)
]

SWITCHES = {
    "1.x": SWITCHES_1x,
    "2.x": SWITCHES_2x,
    "3.x": SWITCHES_2x,
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HttpcontrolCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HttpcontrolSwitch(coordinator, entity)
        for entity in SWITCHES[coordinator.data.model]
        if entity.key in coordinator.data.state
    )

    if coordinator.is_1x():
        async_add_entities([Httpcontrol1xInvertSwitch(coordinator)])

    if coordinator.is_2x():
        async_add_entities([Httpcontrol2xInvertSwitch(coordinator)])

class HttpcontrolSwitch(HttpcontrolEntity, SwitchEntity):
    entity_description: HttpcontrolSwitchDescription

    def __init__(self, coordinator: HttpcontrolCoordinator, description: HttpcontrolSwitchDescription):
        super().__init__(coordinator, description)

    @property
    def is_on(self) -> bool:
        value = bool(int(self.coordinator.data.state[self.entity_description.key]))
        if self._invert():
            value = not value
        return value

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        attrs = super().extra_state_attributes
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
        if self.coordinator.is_1x():
            return bool(int(self.coordinator.data.state.get("out5", 0)))
        elif self.coordinator.is_2x():
            return bool(int(self.coordinator.data.state.get("out6", 0)))
        else:
            return False

class Httpcontrol1xInvertSwitch(HttpcontrolSwitch):
    def __init__(self, coordinator: HttpcontrolCoordinator):
        super().__init__(coordinator, HttpcontrolSwitchDescription(
            key="out5",
            name="Reverse out state",
            entity_category=EntityCategory.CONFIG,
        ))

    @property
    def is_on(self) -> bool:
        return not bool(int(self.coordinator.data.state["out5"]))

    async def async_turn_on(self) -> None:
        self.coordinator.data.state["out5"] = "0"
        await self.coordinator.async_set_out("out", 5)

    async def async_turn_off(self) -> None:
        self.coordinator.data.state["out5"] = "1"
        await self.coordinator.async_set_out("out", 6)

class Httpcontrol2xInvertSwitch(HttpcontrolSwitch):
    def __init__(self, coordinator: HttpcontrolCoordinator):
        super().__init__(coordinator, HttpcontrolSwitchDescription(
            key="out6",
            name="Reverse out state",
            entity_category=EntityCategory.CONFIG,
        ))

    @property
    def is_on(self) -> bool:
        return not bool(int(self.coordinator.data.state["out6"]))

    async def async_turn_on(self) -> None:
        self.coordinator.data.state["out6"] = "0"
        await self.coordinator.async_set_out("out", 6)

    async def async_turn_off(self) -> None:
        self.coordinator.data.state["out6"] = "1"
        await self.coordinator.async_set_out("out", 7)
