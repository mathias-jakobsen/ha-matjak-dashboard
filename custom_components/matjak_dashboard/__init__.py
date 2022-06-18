#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import PLATFORMS
from .matjak import *
from .utils.logger import LOGGER
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant
from typing import Any


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry):
    """ Called when the integration is being setup. """
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry is being set up. """
    async def async_setup(*args: Any) -> None:
        await matjak.async_setup(hass, config_entry)
        config_entry.async_on_unload(config_entry.add_update_listener(async_update_options))
        hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    if hass.is_running:
        await async_setup()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_setup)

    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry is updated. """
    LOGGER.debug("Config entry has been updated. Reloading config entry...")
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry has been unloaded. """
    LOGGER.debug("Config entry is being unloaded...")
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry has been removed. """
    await matjak.async_remove(hass)
    LOGGER.debug("Integration has been removed. Restart Homeassistant to finalize the removal.")