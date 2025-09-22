from __future__ import annotations
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REFRESH_TOKEN, TOKEN_URL

class NetatmoCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # Probe: versuche Token-Refresh einmal
            try:
                async with aiohttp.ClientSession() as session:
                    data = {
                        "grant_type": "refresh_token",
                        "refresh_token": user_input[CONF_REFRESH_TOKEN],
                        "client_id": user_input[CONF_CLIENT_ID],
                        "client_secret": user_input[CONF_CLIENT_SECRET],
                    }
                    async with session.post(TOKEN_URL, data=data, timeout=20) as resp:
                        if resp.status != 200:
                            errors["base"] = "auth"
                        else:
                            js = await resp.json()
                            # Wenn OK, speichern wir die (evtl. neue) refresh_token
                            user_input[CONF_REFRESH_TOKEN] = js.get("refresh_token", user_input[CONF_REFRESH_TOKEN])
                            return self.async_create_entry(title="Netatmo Custom", data=user_input)
            except Exception:
                errors["base"] = "connection"

        schema = vol.Schema({
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_SECRET): str,
            vol.Required(CONF_REFRESH_TOKEN): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)