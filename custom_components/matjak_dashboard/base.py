#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import DASHBOARD_URL
from .utils.config import MatjakConfig
from .utils.frontend import MatjakFrontend
from .utils.logger import LOGGER
from .utils.registry import MatjakRegistry
from .utils.yaml_loader import MatjakYamlLoader
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant
from typing import Callable


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

EVENT_LOVELACE_UPDATED = "lovelace_updated"


#-----------------------------------------------------------#
#       Matjak
#-----------------------------------------------------------#

class Matjak:
    """ A class representing the base integration functionality. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.config: MatjakConfig = MatjakConfig(**{ **config_entry.data, **config_entry.options })
        self.frontend: MatjakFrontend = MatjakFrontend(hass)
        self.hass: HomeAssistant = hass
        self.registry: MatjakRegistry = MatjakRegistry(hass, self.config)
        self.yaml_loader: MatjakYamlLoader = MatjakYamlLoader()


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    async def async_remove(self) -> None:
        """ Removes the integration components. """
        self.yaml_loader.remove()
        self.frontend.remove_dashboard()
        await self.frontend.async_remove_resources()
        self.registry.remove_listeners()

    async def async_setup(self) -> None:
        """ Sets up the integration components. """
        self.yaml_loader.setup(self.registry)
        await self.frontend.async_setup_resources()
        self.frontend.create_dashboard(self.config)

    def reload_config(self, config_entry: ConfigEntry) -> None:
        """ Reloads the config. """
        self.registry.remove_listeners()

        self.config = MatjakConfig(**{ **config_entry.data, **config_entry.options })
        self.registry = MatjakRegistry(self.hass, self.config)
