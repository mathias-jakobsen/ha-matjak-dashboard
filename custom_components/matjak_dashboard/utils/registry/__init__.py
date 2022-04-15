#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import DASHBOARD_URL, VIEWS_PATH
from ..config import MatjakConfig, ViewConfig
from ..logger import LOGGER
from ..user_config import MatjakUserConfig
from homeassistant.core import Event, HomeAssistant
from homeassistant.util.yaml import loader
from typing import Callable
import json
import os


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

UPDATE_INTERVAL = 2


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
        self._hass: HomeAssistant = hass
        self._dict: dict = self._get_dict()
        self._remove_listener: Callable = hass.bus.async_listen("lovelace_updated", self._async_on_lovelace_updated)


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def as_dict(self) -> dict:
        """ Gets the registry as a dictionary. """
        return self._dict

    def remove_listeners(self) -> None:
        """ Removes the listeners. """
        if self._remove_listener:
            self._remove_listener()
            self._remove_listener = None


    #--------------------------------------------#
    #       Event Handlers
    #--------------------------------------------#

    async def _async_on_lovelace_updated(self, e: Event) -> None:
        """ Event handler that is called when lovelace is updated. """
        if e.data.get("url_path", None) == DASHBOARD_URL:
            self._dict = self._get_dict()


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_dict(self) -> dict:
        """ Gets the registry as a dictionary. """
        user_config = self._load_user_config(self._hass.config.path(f"{self._config.config_path}config/"))
        view_configs = self._load_views_config([self._hass.config.path(VIEWS_PATH), self._hass.config.path(f"{self._config.config_path}custom_views/")])

        return {
            "_": {
                "custom_templates_path": self._hass.config.path(f"{self._config.config_path}custom_templates/"),
                "custom_views_path": self._hass.config.path(f"{self._config.config_path}custom_views/"),
                "view_configs": view_configs
            },
            "user_config": user_config
        }

    def _load_views_config(self, paths: list[str]) -> list[ViewConfig]:
        """ Loads the view configurations. """
        result = []

        for path in paths:
            for filename in loader._find_files(path, "*.yaml"):
                if filename.endswith("xx-custom.yaml"):
                    continue

                views = json.loads(json.dumps(loader.load_yaml(filename)))

                for view in views:
                    result.append(ViewConfig(view))

        return result

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