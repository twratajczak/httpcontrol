from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_MODEL,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    ATTR_HW_VERSION,
    ATTR_SW_VERSION,
    CONF_MAC,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .requests import async_get

SKIP_KEYS = ["uptimeSeconds", "uptimeMinutes", "uptimeHours", "uptimeDays", "time", "sec0", "sec1", "sec2", "sec3", "sec4"]


@dataclass
class HttpcontrolData:
    model: str
    hw_version: str
    sw_version: str
    mac: str
    state: dict


class HttpcontrolCoordinator(DataUpdateCoordinator[HttpcontrolData]):
    entry: ConfigEntry
    labels: dict
    rtimes: dict

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.labels = {}
        self.rtimes = {}
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_MAC]}",
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
            always_update=False,
        )

    def is_2x(self) -> bool:
        return self.entry.data[CONF_MODEL] == "2.x"

    def is_3x(self) -> bool:
        return self.entry.data[CONF_MODEL] == "3.x"

    def unique_id(self, key) -> str:
        return f"{self.entry.data[CONF_MAC]}_{key}"

    async def _async_setup(self) -> None:
        if self.is_3x():
            data = await self._async_get("json/status.json")
            tnames = data["tname"].split("*")
            self.labels["dthHum"] = tnames.pop()
            self.labels["dthTemp"] = tnames.pop()
            for i, v in enumerate(tnames):
                self.labels[f"ds{i+1}"] = v
            self.labels["bm280p"] = data.get("pressureName")
            for i in range(0, 6):
                self.labels[f"out{i}"] = data.get(f"oname{i}")
            for i in range(0, 6):
                self.labels[f"inpp{i}"] = data.get(f"iname{i}")
            for i in range(0, 4):
                self.labels[f"pwmd{i}"] = data.get(f"pname{i}")
            for i in range(0, 4):
                self.labels[f"ind{i}"] = data.get(f"idname{i}")
            for i in range(0, 4):
                self.labels[f"power{i}"] = data.get(f"pown{i}")
            for i in enumerate([1, 25, 4, 10]):
                self.labels[f"pm{i}"] = data.get(f"pm{i}name")
            self.labels["co2"] = data.get("co2name")
        else:
            data = await self._async_get("st2.xml")
            names = data["d"].split("*")
            for i in range(0, 5):
                self.labels[f"ia{i+7}"] = names[i]
            for i in range(6, 9):
                self.labels[f"ind{i-5}"] = names[i]
            for i in range(6, 12):
                self.labels[f"out{i-6}"] = data[f"r{i}"]

            for i in range(0, 6):
                if (rtime := data[f"r{i}"]) != "0":
                    self.rtimes[f"out{i}"] = int(rtime)

    async def _async_update_data(self) -> HttpcontrolData:
        try:
            path = "json/status_per.json" if self.is_3x() else "st0.xml"
            state = await self._async_get(path)
            for key in SKIP_KEYS:
                if key in state:
                    del state[key]

            if self.is_3x() and "ind" in state:
                ind = int(state["ind"])
                state["ind0"] = ind & 0b0001
                state["ind1"] = ind & 0b0010
                state["ind2"] = ind & 0b0100
                state["ind3"] = ind & 0b1000
                del state["ind"]

            return HttpcontrolData(
                model=self.entry.data[CONF_MODEL],
                hw_version=self.entry.data[ATTR_HW_VERSION],
                sw_version=self.entry.data[ATTR_SW_VERSION],
                mac=self.entry.data[CONF_MAC],
                state=state,
            )
        except Exception as exc:
            raise UpdateFailed(exc) from exc

    async def async_set_out(self, key: str, state: int):
        resp = await self._async_get(f"outs.cgi?{key}={state}")
        out = resp if isinstance(resp, str) else resp["out"]
        for i, c in enumerate(out):
            self.data.state[f"out{i}"] = c
        self.async_set_updated_data(self.data)

    async def _async_get(self, path: str):
        return await async_get(
            path,
            self.entry.data[CONF_HOST],
            self.entry.data[CONF_USERNAME],
            self.entry.data[CONF_PASSWORD],
            async_get_clientsession(self.hass),
        )

