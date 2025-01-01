from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HttpcontrolCoordinator

class HttpcontrolEntity(CoordinatorEntity[HttpcontrolCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: HttpcontrolCoordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.data.mac)},
            manufacturer="tinycontrol",
            model=coordinator.data.model,
            hw_version=coordinator.data.hw_version,
            sw_version=coordinator.data.sw_version,
        )
        self._attr_unique_id = coordinator.unique_id(description.key)

    @property
    def extra_state_attributes(self):
        attrs = {}
        if name := self.coordinator.labels.get(self.entity_description.key):
            attrs["Name"] = name
        return attrs
