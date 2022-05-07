#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import PARSER_KEY_GLOBAL
from ...utils.logger import LOGGER
from ..config import MJ_Config
from ..user_config import MJ_UserConfig
from .areas import AreaRegistry
from .entities import EntityRegistry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.util.yaml import loader
from typing import Any, Callable
import os


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

UPDATE_INTERVAL = 3.5


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_registry: dict = None
_timer_remove_listener: Callable = None


#-----------------------------------------------------------#
#       Getters
#-----------------------------------------------------------#

def get_registry(hass: HomeAssistant, config: MJ_Config) -> dict:
    """ Gets the registry. """
    global _registry

    if _registry is None or _timer_remove_listener is None:
        _timer_remove_listener = async_call_later(hass, UPDATE_INTERVAL, _async_on_timer_expired)
        _registry = _get_registry(hass, config)

    return _registry


#-----------------------------------------------------------#
#       Private Event Handlers
#-----------------------------------------------------------#

async def _async_on_timer_expired(*args: Any) -> None:
    """ Triggered when the update timer has expired. """
    global _timer_remove_listener
    _timer_remove_listener = None


#-----------------------------------------------------------#
#       Private Functions
#-----------------------------------------------------------#

def _get_registry(hass: HomeAssistant, config: MJ_Config) -> dict:
    """ Gets the registry. """
    user_config = _load_user_config(hass.config.path(f"{config.user_config_path}config/"))
    areas = AreaRegistry(hass, user_config)
    entities = EntityRegistry(hass, areas, user_config)

    return {
        PARSER_KEY_GLOBAL: {
            "areas": {},
            "devices": {},
            "entities": entities,
            "paths": {
                "custom_button_card_templates": hass.config.path(f"{config.user_config_path}", "custom_templates/"),
                "custom_views": hass.config.path(f"{config.user_config_path}", "custom_views/")
            }
        }
    }

def _load_user_config(path: str) -> MJ_UserConfig:
    """ Loads the user configuration from the configuration directory. """
    result = {}

    if os.path.exists(path):
        for filename in loader._find_files(path, "*.yaml"):
            config = loader.load_yaml(filename)

            if isinstance(config, dict):
                result.update(config)

        result = MJ_UserConfig.get_schema()(result)
        LOGGER.debug(f"User configuration loaded from {path}.")
    else:
        LOGGER.warning(f"Unable to load user configuration: Path {path} does not exist.")

    return MJ_UserConfig(result)