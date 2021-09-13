#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import loader
from logging import getLogger
from typing import Any, Dict
import os
import voluptuous as vol


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

DEFAULT_WEATHER_ICONS = {
    "fog": "mdi:weather-fog",
    "sunny": "mdi:weather-sunny"
}


#-----------------------------------------------------------#
#       Validation Functions
#-----------------------------------------------------------#

def validate_weather_icons(value: Dict[str, str]):
    """ Validates the weather icons. """
    vol.Schema({str: str})(value)
    return {**DEFAULT_WEATHER_ICONS, **value}


#-----------------------------------------------------------#
#       Schemas
#-----------------------------------------------------------#

USER_CONFIG_SCHEMA = vol.Schema({
    vol.Required("areas", default={}): {str: {
        vol.Optional("icon"): str,
        vol.Optional("location"): str,
        vol.Required("priority", default=1): int
    }},
    vol.Required("area_locations", default={}): {
        vol.Optional("icon"): str,
        vol.Required("priority", default=1): int
    },
    vol.Required("exclude", default={}): {
        vol.Required("areas", default=[]): [str],
        vol.Required("devices", default=[]): [str],
        vol.Required("entities", default=[]): [str],
    },
    vol.Required("weather", default={}): {
        vol.Required("icons", default=DEFAULT_WEATHER_ICONS): validate_weather_icons
    }
}, extra=True)


#-----------------------------------------------------------#
#       Public Functions
#-----------------------------------------------------------#

def load_config(hass: HomeAssistant, config_path: str) -> Dict[str, Any]:
    """ Loads the user configuration from the configuration directory. """
    if config_path is None:
        return USER_CONFIG_SCHEMA({})

    result = {}
    path = hass.config.path(config_path)

    if os.path.exists(path):
        dashboard_config = {}

        for filename in loader._find_files(path, "*.yaml"):
            config = loader.load_yaml(filename)

            if isinstance(config, dict):
                dashboard_config.update(config)

        result.update(dashboard_config)

    return USER_CONFIG_SCHEMA(result)
