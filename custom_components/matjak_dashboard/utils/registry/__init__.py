#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import (
    CONF_CONFIG_PATH,
    CONF_LANGUAGE,
    DASHBOARD_URL,
    PARSER_KEY_GLOBAL
)
from ..helpers import get_button_card_template, get_button_card_template_list, get_translations
from ..user_config import load_config
from .areas import Areas
from .devices import Devices
from .entities import Entities
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.event import async_call_later
from logging import getLogger
from typing import Any, Dict


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__package__)


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_registry = {}
_reload = None
_remove_listener = None
_timer_remove_listener = None


#-----------------------------------------------------------#
#       Event Handlers
#-----------------------------------------------------------#

async def _async_on_timer_ended(e: Event) -> None:
    """ Called when the first call timer expires. """
    global _reload
    _reload = True

async def _async_on_lovelace_updated(e: Event) -> None:
    """ Event handler that is called when lovelace is updated. """
    global _reload
    if e.data.get("url_path", None) == DASHBOARD_URL:
        _reload = True

def _get_registry(hass: HomeAssistant, config_entry: ConfigEntry) -> Dict[str, Any]:
    """ Gets the registry. """
    language = config_entry.options.get(CONF_LANGUAGE, config_entry.data.get(CONF_LANGUAGE))
    user_config_path = config_entry.options.get(CONF_CONFIG_PATH, config_entry.data.get(CONF_CONFIG_PATH))

    button_card_template_list = get_button_card_template_list(hass)
    translations = get_translations(hass, language)
    user_config = load_config(hass, user_config_path)

    areas = Areas(hass, user_config)
    devices = Devices(hass, user_config, areas)
    entities = Entities(hass, user_config, areas, devices)

    return {
        PARSER_KEY_GLOBAL: {
            "button_card_template_list": button_card_template_list,
            "get_button_card_template": get_button_card_template(hass, button_card_template_list),
            "config": user_config,
            "dashboard_url": DASHBOARD_URL,
            "registry": {
                "areas": areas,
                "devices": devices,
                "entities": entities
            },
            "translations": translations
        }
    }


#-----------------------------------------------------------#
#       Functions
#-----------------------------------------------------------#

def remove_listeners() -> None:
    """ Removes all listeners relevant to the user configuration. """
    global _remove_listener
    _remove_listener and _remove_listener()
    _remove_listener = None

def setup_listeners(hass: HomeAssistant) -> None:
    """ Sets up all listeners relevant to the user configuration. """
    global _remove_listener
    remove_listeners()
    _remove_listener = hass.bus.async_listen("lovelace_updated", _async_on_lovelace_updated)


#-----------------------------------------------------------#
#       Functions
#-----------------------------------------------------------#

def get_registry(hass: HomeAssistant, config_entry: ConfigEntry) -> Dict[str, Any]:
    """ Gets the registry. """
    global _registry, _reload, _timer_remove_listener

    if _reload is None:
        _timer_remove_listener and _timer_remove_listener()
        _timer_remove_listener = async_call_later(hass, 1.5, _async_on_timer_ended)

    if _reload != False:
        _registry = _get_registry(hass, config_entry)
        _reload = False

    return _registry

def remove_listeners() -> None:
    """ Removes all listeners relevant to the registry. """
    global _remove_listener
    _remove_listener and _remove_listener()
    _remove_listener = None

def setup_listeners(hass: HomeAssistant) -> None:
    """ Sets up all listeners relevant to the registry. """
    global _remove_listener
    remove_listeners()
    _remove_listener = hass.bus.async_listen("lovelace_updated", _async_on_lovelace_updated)
