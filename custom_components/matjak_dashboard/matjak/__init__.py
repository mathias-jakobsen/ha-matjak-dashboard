#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DOMAIN
from ..utils.logger import LOGGER
from .config import MJ_Config
from .frontend import *
from .yaml_loader import *
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant
from typing import Any


#-----------------------------------------------------------#
#       Matjak
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Sets up the required components. """
    async def async_setup(*args: Any) -> None:
        config = hass.data[DOMAIN] = MJ_Config(**{**config_entry.data, **config_entry.options})
        await frontend.async_setup(hass, config)
        yaml_loader.setup(hass, config)

    if hass.is_running:
        await async_setup()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_setup)

async def async_reload(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Reloads the components. """
    if DOMAIN not in hass.data:
        return await async_setup(hass, config_entry)

    old_config = hass.data[DOMAIN]
    new_config = hass.data[DOMAIN] = MJ_Config(**{**config_entry.data, **config_entry.options})

    await frontend.async_reload(hass, old_config, new_config)
    yaml_loader.reload(hass, new_config)

async def async_remove(hass: HomeAssistant) -> None:
    """ Removes the components. """
    if DOMAIN not in hass.data:
        return

    frontend.async_remove(hass, hass.data[DOMAIN])
    yaml_loader.remove()