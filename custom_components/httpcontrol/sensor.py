from dataclasses import dataclass
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfTemperature,
    UnitOfPressure,
    EntityCategory,
)
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HttpcontrolData, HttpcontrolCoordinator
from .entity import HttpcontrolEntity

PARALLEL_UPDATES = 0

@dataclass(frozen=True, kw_only=True)
class HttpcontrolSensorDescription(SensorEntityDescription):
    entity_category: str = None
    entity_registry_enabled_default: bool = False
    state_class: str = SensorStateClass.MEASUREMENT
    value_fn: Callable = lambda x: int(x)
    suggested_display_precision=1

SENSORS_1x = [
    HttpcontrolSensorDescription(
        key="ia0",
        name="Board Temperature",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia1",
        name="Board Voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia2",
        name="Inp1",
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia4",
        name="Inp3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia5",
        name="Inp4",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0,
    ),
    *[
        HttpcontrolSensorDescription(
            key=f"ia{i+1}",
            name=f"Inp{i}",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            value_fn = lambda x: int(x) / 10.0 if -50 <= int(x) <= 850 else None,
        )
        for i in [2, 6, 7, 8, 9, 10, 11]
    ],
    HttpcontrolSensorDescription(
        key="ia13",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia14",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia17",
        name="INP4D measure",
        suggested_display_precision=3,
        value_fn = lambda x: int(x) / 1000.0,
    ),
]

SENSORS_2x = [
    HttpcontrolSensorDescription(
        key="ia0",
        name="Board Temperature",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia1",
        name="Board Voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia2",
        name="Inp1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0,
    ),
    HttpcontrolSensorDescription(
        key="ia3",
        name="Inp2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0,
    ),
    HttpcontrolSensorDescription(
        key="ia4",
        name="Inp3",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn = lambda x: int(x) / 10.0 if -30 <= int(x) <= 420 else None,
    ),
    HttpcontrolSensorDescription(
        key="ia5",
        name="Inp4",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0,
    ),
    HttpcontrolSensorDescription(
        key="ia6",
        name="Inp5",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn = lambda x: int(x) / 10.0,
    ),
    *[
        HttpcontrolSensorDescription(
            key=f"ia{i}",
            name=f"Inp{i-1}",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            suggested_display_precision=1,
            value_fn=lambda x: int(x) / 10.0 if x != "-600" else None,
        )
        for i in range(7, 13)
    ],
    HttpcontrolSensorDescription(
        key="ia13",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia14",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn = lambda x: int(x) / 10.0,
    ),
    HttpcontrolSensorDescription(
        key="ia17",
        name="INP4D measure",
        suggested_display_precision=3,
        value_fn = lambda x: int(x) / 1000.0,
    ),
]
SENSORS_3x = [
    HttpcontrolSensorDescription(
        key="tem",
        name="Board Temperature",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0,
    ),
    HttpcontrolSensorDescription(
        key="vin",
        name="Board Voltage",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0,
    ),
    HttpcontrolSensorDescription(
        key="dthTemp",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn = lambda x: int(x) / 10.0 if x != "-600" else None,
    ),
    HttpcontrolSensorDescription(
        key="dthHum",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn = lambda x: int(x) / 10.0 if x != "-600" else None,
    ),
    HttpcontrolSensorDescription(
        key="bm280p",
        name="Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        suggested_display_precision=2,
        value_fn = lambda x: int(x) / 100.0 if x != "-600" else None,
    ),
    *[
        HttpcontrolSensorDescription(
            key=f"diff{i}",
            name=f"DIFF{i}",
            suggested_display_precision=3,
            value_fn=lambda x: int(x),
        )
        for i in range(1, 4)
    ],
    *[
        HttpcontrolSensorDescription(
            key=f"ds{i}",
            name=f"DS{i}",
            value_fn=lambda x: int(x) / 10.0 if x != "-600" else None,
        )
        for i in range(1, 9)
    ],
    *[
        HttpcontrolSensorDescription(
            key=f"inpp{i}",
            name=f"Input {i}",
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda x: int(x) / 100.0,
        )
        for i in range(1, 7)
    ],
]

SENSORS = {
    "1.x": SENSORS_1x,
    "2.x": SENSORS_2x,
    "3.x": SENSORS_3x,
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HttpcontrolCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HttpcontrolSensor(coordinator, entity)
        for entity in SENSORS[coordinator.data.model]
        if entity.key in coordinator.data.state
    )

class HttpcontrolSensor(HttpcontrolEntity, SensorEntity):
    entity_description: HttpcontrolSensorDescription

    def __init__(self, coordinator: HttpcontrolCoordinator, description: HttpcontrolSensorDescription):
        super().__init__(coordinator, description)
        if "ia17" == description.key:
            self._attr_native_unit_of_measurement = coordinator.measure_unit

    @property
    def native_value(self) -> float | int | None:
        return self.entity_description.value_fn(self.coordinator.data.state[self.entity_description.key])
