#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .utils import registry
from .utils.const import (
    DOMAIN,
    PLATFORMS,
    REQUIREMENTS
)
from .utils.dashboard import create_dashboard, remove_dashboard
from .utils.resources import async_create_resources, async_remove_resources
from .utils.yaml_loader import setup_yaml_loader
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import IntegrationError
from logging import getLogger
from typing import Any, Dict


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__package__)
UNDO_LISTENERS = "undo_listeners"


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config: Dict[Any, str]) -> bool:
    unmet_requirments = [requirement for requirement in REQUIREMENTS if requirement not in config]

    if len(unmet_requirments) > 0:
        raise IntegrationError(f"Integration requirements not met: {unmet_requirments}")

    if DOMAIN in config:
        raise IntegrationError(f"{DOMAIN} can only be loaded from the UI. Remove {DOMAIN} from your YAML configuration.")

    await async_create_resources(hass)
    registry.setup_listeners(hass)

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    data = hass.data.setdefault(DOMAIN, {})

    data[config_entry.entry_id] = { UNDO_LISTENERS: [] }
    data[config_entry.entry_id][UNDO_LISTENERS].append(config_entry.add_update_listener(async_update_options))

    for platform in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, platform))

    setup_yaml_loader(hass, config_entry)
    create_dashboard(hass, config_entry)

    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    unload_ok = all(
        [
            await hass.config_entries.async_forward_entry_unload(config_entry, platform)
            for platform in PLATFORMS
        ]
    )

    data = hass.data[DOMAIN]

    while data[config_entry.entry_id][UNDO_LISTENERS]:
        data[config_entry.entry_id][UNDO_LISTENERS].pop()()

    if unload_ok:
        data.pop(config_entry.entry_id)
        remove_dashboard(hass)

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    await async_remove_resources(hass)
    registry.remove_listeners()
    hass.async_create_task(hass.services.async_call("browser_mod", "toast", { "duration": 3000, "message": f"Restart Homeassistant to finalize uninstallation of {DOMAIN}." }))