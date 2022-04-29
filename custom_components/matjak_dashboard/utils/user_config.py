#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DOMAIN
from .logger import LOGGER
from dataclasses import dataclass, field
from typing import Optional
import voluptuous as vol


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

DEFAULT_WEATHER_ICONS = {
    "cloudy": "mdi:weather-cloudy",
    "fog": "mdi:weather-fog",
    "partlycloudy": "mdi:weather-partly-cloudy",
    "pouring": "mdi:weather-pouring",
    "rainy": "mdi:weather-rainy",
    "sunny": "mdi:weather-sunny"
}


#-----------------------------------------------------------#
#       Validation Functions
#-----------------------------------------------------------#

def validate_weather_icons(value: dict[str, str]) -> dict:
    """ Validates the weather icons. """
    vol.Schema({str: str})(value)
    return {**DEFAULT_WEATHER_ICONS, **value}



#-----------------------------------------------------------#
#       MatjakConfig - Areas
#-----------------------------------------------------------#

@dataclass
class AreasUserConfig:
    """ A class representing the areas user configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    priority: int = 1
    icon: str = field(default=None)
    location: str = field(default=None)


#-----------------------------------------------------------#
#       MatjakConfig - AreaLocations
#-----------------------------------------------------------#

@dataclass
class AreaLocationsConfig:
    """ A class representing the area locations user configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    priority: int = 1
    icon: str = field(default=None)


#-----------------------------------------------------------#
#       MatjakConfig - Domains
#-----------------------------------------------------------#

@dataclass
class DomainsConfig:
    """ A class representing the area locations user configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    icon: str = None
    priority: int = 1



#-----------------------------------------------------------#
#       MatjakConfig - Exclude
#-----------------------------------------------------------#

@dataclass
class ExcludeConfig:
    """ A class representing the exclude user configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: list[str] = field(default_factory=list)
    devices: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)



#-----------------------------------------------------------#
#       MatjakConfig
#-----------------------------------------------------------#

class MatjakUserConfig:
    """ A class representing the user configuration. """

    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @staticmethod
    def get_schema() -> vol.Schema:
        """ Gets the voluptuous schema. """
        return vol.Schema({
            vol.Required("areas", default={}): {str: {
                vol.Optional("icon"): str,
                vol.Optional("location"): str,
                vol.Optional("priority"): int
            }},
            vol.Required("area_locations", default={}): {
                vol.Optional("icon"): str,
                vol.Optional("priority"): int
            },
            vol.Required("exclude", default={}): {
                vol.Required("areas", default=[]): [str],
                vol.Required("devices", default=[]): [str],
                vol.Required("entities", default=[]): [str],
            },
            vol.Required("favorite_entities", default=[]): [str],
            vol.Required("favorite_scenes", default=[]): [str],
            vol.Required("weather", default={}): {
                vol.Required("entities", default={}): {str: str},
                vol.Required("icons", default=DEFAULT_WEATHER_ICONS): validate_weather_icons
            },
            vol.Required("domains", default={}): {
                str: {
                    vol.Optional("icon"): str,
                    vol.Required("priority", default=1): int
                }
            }
        }, extra=True)


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: dict[str, AreasUserConfig]
    area_locations: dict[str, AreaLocationsConfig]
    domains: dict[str, DomainsConfig]
    exclude: ExcludeConfig


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config: dict):
        self.areas = { key: AreasUserConfig(**value) for key, value in config.pop("areas", {}).items() }
        self.area_locations = { key: AreaLocationsConfig(**value) for key, value in config.pop("area_locations", {}).items() }
        self.domains = { key: DomainsConfig(**value) for key, value in config.pop("domains", {}).items() }
        self.exclude = ExcludeConfig(**config.pop("exclude", {}))

        for key, value in config.items():
            setattr(self, key, value)


