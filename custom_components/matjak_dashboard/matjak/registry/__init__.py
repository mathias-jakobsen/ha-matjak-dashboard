#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import PARSER_KEY_GLOBAL, TRANSLATIONS_PATH
from ...utils.logger import LOGGER
from ..config import MJ_Config
from ..user_config import MJ_UserConfig
from .areas import AreaRegistry
from .domains import DomainRegistry
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
    global _registry, _timer_remove_listener

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
    domains = DomainRegistry(hass, user_config)
    entities = EntityRegistry(hass, areas, user_config)
    translations = _load_translations(hass.config.path(TRANSLATIONS_PATH, f"{config.language}.yaml"))

    return {
        PARSER_KEY_GLOBAL: {
            "areas": areas,
            "button_card_templates": _load_button_card_templates(hass.config.path("custom_components/matjak_dashboard/lovelace/templates/button_card")),
            "domains": domains,
            "entities": entities,
            "paths": {
                "custom_button_card_templates": hass.config.path(f"{config.user_config_path}", "custom_templates/"),
                "custom_views": hass.config.path(f"{config.user_config_path}", "custom_views/")
            },
            "translations": translations,
            "user_config": user_config
        }
    }

def _load_button_card_templates(path: str) -> list[str]:
    """ Loads a list of available button card templates. """
    result = []

    for filename in loader._find_files(path, "*.yaml"):
        if filename.endswith("__custom__.yaml"):
            continue

        templates = loader.load_yaml(filename).keys()
        result.extend(templates)

    return result

def _load_translations(path: str) -> dict[str, str]:
    """ Loads the translation strings. """
    if os.path.exists(path):
        with open(path, encoding="utf-8") as file:
            return loader.yaml.load(file, Loader=lambda stream: loader.SafeLineLoader(stream, None)) or {}

    return {}

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