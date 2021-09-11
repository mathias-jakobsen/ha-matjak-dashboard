# -----------------------------------------------------------#
#       Imports
# -----------------------------------------------------------#

from homeassistant.core import Event, HomeAssistant
from logging import getLogger
from typing import Any, Dict
import voluptuous as vol

LOGGER = getLogger(__package__)


# -----------------------------------------------------------#
#       Defaults
# -----------------------------------------------------------#

DEFAULT_AREA_ICON = "mdi:texture-box"
DEFAULT_AREA_ICONS = {
    "mdi:baby": ["Child's Room", "Børneværelse"],
    "mdi:bed-king": ["Bedroom", "Soveværelse"],
    "mdi:bike": ["Bike Room", "Cykelrum"],
    "mdi:toilet": ["Bathroom", "Badeværelse"],
    "mdi:garage": ["Garage"],
    "mdi:coat-rack": ["Entrance", "Hallway", "Gang", "Entré", "Entre"],
    "mdi:silverware-fork-knife": ["Dining Room", "Spisestue"],
    "mdi:pot-steam": ["Kitchen", "Køkken"],
    "mdi:sofa": ["Living Room", "Stue"],
    "mdi:chair-rolling": ["Office", "Kontor"],
    "mdi:bed": ["Guest Room", "Gæsteværelse"],
    "mdi:washing-machine": ["Utility Room", "Bryggers"],
    "mdi:wardrobe": ["Walk In", "Wardrobe", "Garderobe"]
}

DEFAULT_WEATHER_ICONS = {
    "fog": "mdi:weather-fog",
    "sunny": "mdi:weather-sunny"
}


# -----------------------------------------------------------#
#       Validation Functions
# -----------------------------------------------------------#

def validate_weather_icons(value: Dict[str, str]):
    """ Validates the weather icons. """
    vol.Schema({str: str})(value)
    return {**DEFAULT_WEATHER_ICONS, **value}


# -----------------------------------------------------------#
#       Schemas
# -----------------------------------------------------------#

USER_CONFIG_SCHEMA = vol.Schema({
    vol.Required("areas", default={}): {str: {
        vol.Optional("icon"): str,
        vol.Optional("location"): str,
        vol.Required("priority", default=1): int
    }},
    vol.Required("area_locations", default=[]): [str],
    vol.Required("weather", default={}): {
        vol.Required("icons", default=DEFAULT_WEATHER_ICONS): validate_weather_icons
    }
})


# -----------------------------------------------------------#
#       UserConfig
# -----------------------------------------------------------#

_config = {}
_reload_config = True

def get_config(hass: HomeAssistant) -> Dict[str, Any]:
    if _reload_config:
        _config = _load_config(hass)

    return _config

class UserConfig:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self.listeners = []
        self.setup_listeners()

    def remove_listeners(self) -> None:
        while self.listeners:
            self.listeners.pop()()

    def setup_listeners(self) -> None:
        self.remove_listeners()
        self.listeners.append(self.hass.bus.async_listen("lovelace_updated", self._async_on_lovelace_updated))

    async def _async_on_lovelace_updated(self, e: Event) -> None:
        LOGGER.error("lovelace updated")