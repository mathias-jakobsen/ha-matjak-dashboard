#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..config import MatjakConfig
from ..logger import LOGGER
from ..user_config import MatjakUserConfig
from .areas import Areas
from .devices import Devices
from .domains import Domains
from .entities import Entities
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.util.yaml import loader
from typing import Callable
import os


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

UPDATE_INTERVAL = 3


#-----------------------------------------------------------#
#       MatjakRegistry
#-----------------------------------------------------------#

class MatjakRegistry:
    """ A class representing the registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MatjakConfig):
        self._config: MatjakConfig = config
        self._dict: dict = None
        self._hass: HomeAssistant = hass
        self._last_update_listener: Callable = None


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def as_dict(self) -> dict:
        """ Gets the registry as a dictionary. """
        if self._dict is None or self._last_update_listener is None:
            self._last_update_listener = async_call_later(self._hass, UPDATE_INTERVAL, self._async_on_update_timer_ended)
            self._dict = self._get_dict()

        return self._dict

    def remove_listeners(self) -> None:
        """ Removes the listeners. """
        if self._last_update_listener:
            self._last_update_listener()
            self._last_update_listener = None


    #--------------------------------------------#
    #       Event Handlers
    #--------------------------------------------#

    async def _async_on_update_timer_ended(self, e: Event) -> None:
        """ Triggered when the update delay timer has expired. """
        self._last_update_listener = None


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_dict(self) -> dict:
        """ Gets the registry as a dictionary. """
        user_config = self._load_user_config(self._hass.config.path(f"{self._config.config_path}config/"))

        areas = Areas(self._hass, user_config)
        devices = Devices(self._hass, user_config, areas)
        entities = Entities(self._hass, user_config, areas, devices)

        return {
            "_": {
                "custom_templates_path": self._hass.config.path(f"{self._config.config_path}custom_templates/"),
                "custom_views_path": self._hass.config.path(f"{self._config.config_path}custom_views/"),
            },
            "registry": {
                "areas": areas,
                "devices": devices,
                "domains": Domains(self._hass, user_config),
                "entities": entities
            },
            "user_config": user_config
        }

    def _load_user_config(self, path) -> MatjakUserConfig:
        """ Loads the user configuration from the configuration directory. """
        result = {}

        if os.path.exists(path):
            for filename in loader._find_files(path, "*.yaml"):
                config = loader.load_yaml(filename)

                if isinstance(config, dict):
                    result.update(config)

            result = MatjakUserConfig.get_schema()(result)
            LOGGER.debug(f"User configuration loaded from {path}config/")
        else:
            LOGGER.warning(f"Unable to load user configuration: Path {path}config/ does not exist.")

        return MatjakUserConfig(result)