#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .base import Matjak
from .const import (
    DOMAIN,
    PLATFORMS
)
from .utils.logger import LOGGER
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import HomeAssistant
from typing import Any


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry has been set up. """
    async def async_setup(*args: Any) -> None:
        LOGGER.debug("Initializing config entry...")

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = Matjak(hass, config_entry)

        matjak_dashboard: Matjak = hass.data[DOMAIN]
        await matjak_dashboard.async_setup()

        config_entry.async_on_unload(config_entry.add_update_listener(async_update_options))
        hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

        LOGGER.debug("Config entry has been initialized!")

    if hass.is_running:
        await async_setup()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, async_setup)

    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry is updated. """
    LOGGER.debug("Config entry has been updated. Reloading config entry...")
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry has been unloaded. """
    LOGGER.debug("Config entry is being unloaded...")
    matjak_dashboard: Matjak = hass.data[DOMAIN]
    matjak_dashboard.reload_config(config_entry)
    matjak_dashboard.frontend.remove_dashboard()
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry has been removed. """
    matjak_dashboard: Matjak = hass.data[DOMAIN]
    await matjak_dashboard.async_remove()
    hass.data.pop(DOMAIN)
    LOGGER.debug("Integration has been removed. Restart Homeassistant to finalize the removal.")