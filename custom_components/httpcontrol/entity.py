from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HttpcontrolCoordinator


class HttpcontrolEntity(CoordinatorEntity[HttpcontrolCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: HttpcontrolCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.data.mac)},
            manufacturer="tinycontrol",
            model=coordinator.data.model,
            hw_version=coordinator.data.hw_version,
            sw_version=coordinator.data.sw_version,
        )
