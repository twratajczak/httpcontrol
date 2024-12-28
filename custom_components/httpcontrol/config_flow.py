from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_MODEL,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    ATTR_HW_VERSION,
    ATTR_SW_VERSION,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .const import DOMAIN
from .requests import async_get, HttpcontrolAuthError

class HttpcontrolFlowHandler(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    host: str
    username: str
    password: str
    mac: str
    name: str
    hw_version: str
    sw_version: str
    model: str
    scan_interval: int

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=self._schema())

        self.host = user_input[CONF_HOST]
        self.username = user_input[CONF_USERNAME]
        self.password = user_input[CONF_PASSWORD]
        self.scan_interval = user_input[CONF_SCAN_INTERVAL]

        errors = {}
        try:
            await self._async_get_version(raise_on_progress=False)
        except HttpcontrolAuthError:
            errors[CONF_USERNAME] = "invalid_auth"
            errors[CONF_PASSWORD] = "invalid_auth"
        if errors:
            return self.async_show_form(step_id="user", data_schema=self._schema(), errors=errors)
        return self.async_create_entry(title=self.name, data=self._to_data())

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        config = self._get_reconfigure_entry()
        if user_input is None:
            return self.async_show_form(step_id="reconfigure", data_schema=self._schema(config.data))
        return self.async_update_reload_and_abort(config, data_updates=user_input)

    async def _async_get_version(self, raise_on_progress: bool = True) -> None:
        try:
          all = await self._async_get("json/all.json")
          self.model = "3.x"
          self.mac = format_mac(all["mac"])
          self.hw_version = all["hw"]
          self.sw_version = all["sw"]
          network = await self._async_get("json/network.json")
          self.name = network["sname"]
        except:
          board = await self._async_get("board.xml")
          self.model = "2.x"
          self.mac = format_mac(board["b6"])
          self.name = board["b7"]
          st2 = await self._async_get("st2.xml")
          self.hw_version = "2." + st2["hw"]
          self.sw_version = st2["ver"]
        await self.async_set_unique_id(self.mac, raise_on_progress=raise_on_progress)
        self._abort_if_unique_id_configured(updates=self._to_data())

    async def _async_get(self, path: str):
        session = async_get_clientsession(self.hass)
        return await async_get(path, self.host, self.username, self.password, session)

    @callback
    def _schema(self, data = {}):
        return vol.Schema({
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Optional(CONF_USERNAME, default=data.get(CONF_USERNAME)): str,
            vol.Optional(CONF_PASSWORD, default=data.get(CONF_PASSWORD)): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=data.get(CONF_SCAN_INTERVAL, 30)): vol.All(int, vol.Range(min=1)),
        })

    @callback
    def _to_data(self) -> dict[str, Any]:
        return {
            CONF_MODEL: self.model,
            CONF_HOST: self.host,
            CONF_USERNAME: self.username,
            CONF_PASSWORD: self.password,
            CONF_MAC: self.mac,
            ATTR_HW_VERSION: self.hw_version,
            ATTR_SW_VERSION: self.sw_version,
            CONF_SCAN_INTERVAL: self.scan_interval,
        }
