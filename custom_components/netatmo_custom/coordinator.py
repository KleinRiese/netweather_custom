from __future__ import annotations
import asyncio
import aiohttp
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import (DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REFRESH_TOKEN, TOKEN_URL, STATIONS_URL, UPDATE_INTERVAL_SECONDS)

def _flatten(prefix, obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten(f"{prefix}.{k}" if prefix else k, v, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _flatten(f"{prefix}.{i}", v, out)
    else:
        out[prefix] = obj

class NetatmoDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            hass.helpers.logger.logger.getChild(DOMAIN),
            name="Netatmo Custom Coordinator",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.entry = entry

    async def _async_refresh_token(self, session: aiohttp.ClientSession) -> str:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.entry.data[CONF_REFRESH_TOKEN],
            "client_id": self.entry.data[CONF_CLIENT_ID],
            "client_secret": self.entry.data[CONF_CLIENT_SECRET],
        }
        async with session.post(TOKEN_URL, data=data, timeout=20) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise UpdateFailed(f"Token refresh failed: {resp.status} {text}")
            js = await resp.json()
            new_refresh = js.get("refresh_token")
            if new_refresh and new_refresh != self.entry.data[CONF_REFRESH_TOKEN]:
                self.hass.config_entries.async_update_entry(self.entry, data={**self.entry.data, CONF_REFRESH_TOKEN: new_refresh})
            return js["access_token"]

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                access_token = await self._async_refresh_token(session)
                headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
                async with session.get(STATIONS_URL, headers=headers, timeout=20) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise UpdateFailed(f"Stations fetch failed: {resp.status} {text}")
                    js = await resp.json()
            # Flatten
            flat = {}
            _flatten("", js, flat)
            return flat
        except Exception as err:
            raise UpdateFailed(str(err)) from err
