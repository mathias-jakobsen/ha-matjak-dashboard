#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .base import BaseRegistry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry
from logging import getLogger
from typing import Any, Dict, List, Tuple, Union


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

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

LOGGER = getLogger(__package__)


#-----------------------------------------------------------#
#       Class - Areas
#-----------------------------------------------------------#

class Areas(BaseRegistry[area_registry.AreaEntry]):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        exclude_keys = ["id", "name"]
        exclude_values = config.get("exclude", {}).get("areas", [])
        registry = self._filter_registry(area_registry.async_get(hass).areas, exclude_keys, exclude_values)

        self.config = config
        self.hass = hass
        self.registry = self._sort_registry(registry, config)


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _sort_registry(self, registry: Dict[str, area_registry.AreaEntry], config: Dict[str, Any]) -> Dict[str, area_registry.AreaEntry]:
        """ Returns a registry sorted by priority and name. """
        area_config = config.get("areas", {})
        sorted_areas = sorted(registry.items(), key=lambda x: (area_config.get(x[0], area_config.get(x[1].name, {})).get("priority", 1), x[0]))

        return dict(sorted_areas)


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_area_icon(self, area_entry: area_registry.AreaEntry) -> str:
        """ Gets the icon associated with the area. """
        area_config = self.config.get("areas", {}).get(area_entry.id, self.config.get("areas", {}).get(area_entry.name, {}))

        if "icon" in area_config:
            return area_config["icon"]

        icon_match = next(filter(lambda x: area_entry.id in x[1] or area_entry.name in x[1], DEFAULT_AREA_ICONS.items()), None)

        if icon_match:
            return icon_match[0]

        return DEFAULT_AREA_ICON

    def get_by_name(self, name: str) -> Union[area_registry.AreaEntry, None]:
        """ Gets an area by its name. """
        return next((area for area in self.registry.values() if area.name == name), None)

    def group_by_location(self) -> Tuple[str, List[area_registry.AreaEntry]]:
        """ Gets a dictionary of areas grouped by their location. """
        result = {}

        area_config = self.config.get("areas", {})
        location_config = self.config.get("area_locations", {})

        for area in self.registry.values():
            location = area_config.get(area.id, area_config.get(area.name, {})).get("location", "__others__")

            if location not in result:
                result[location] = []

            result[location].append(area)

        return sorted(result.items(), key=lambda x: (location_config.get(x[0], {}).get("priority", 1), x[0]))
