#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import AreaConfig, MJ_UserConfig
from dataclasses import dataclass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.area_registry import async_get as async_get_areas


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


#-----------------------------------------------------------#
#       EntityRegistryEntry
#-----------------------------------------------------------#

@dataclass
class AreaRegistryEntry:
    """ A class representing an area entry. """
    icon: str | None
    id: str
    location: str | None
    name: str | None


#-----------------------------------------------------------#
#       AreaRegistry
#-----------------------------------------------------------#

class AreaRegistry:
    """ A class representing an area registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MJ_UserConfig):
        self._areas: dict[str, AreaRegistryEntry] = self._get_areas(hass, config)
        self._config: MJ_UserConfig = config
        self._hass: HomeAssistant = hass


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for entry in self._areas.values():
            yield entry


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_areas(self, hass: HomeAssistant, config: MJ_UserConfig):
        """ Gets a dictionary containing the area entries. """
        area_registry = async_get_areas(hass).areas
        result = {}

        for area in area_registry.values():
            if area.id in config.exclude.areas or area.name in config.exclude.areas:
                continue

            area_config = config.areas.get(area.id, config.areas.get(area.name, AreaConfig()))
            new_entry = AreaRegistryEntry(
                icon=area_config.icon,
                id=area.id,
                name=area.name,
                location=area_config.location
            )

            if new_entry.icon is None:
                new_entry.icon = self._get_area_icon(new_entry)

            result[new_entry.id] = new_entry

        return result


    def _get_area_icon(self, area: AreaRegistryEntry) -> str:
        """ Gets the icon for an area. """
        icon_match = next(filter(lambda x: area.id in x[1] or area.name in x[1], DEFAULT_AREA_ICONS.items()), None)

        if icon_match:
            return icon_match[0]

        return DEFAULT_AREA_ICON


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_id(self, id: str) -> AreaRegistryEntry | None:
        """ Gets an area by id. """
        return self._areas.get(id, None)

    def get_by_name(self, name: str) -> AreaRegistryEntry | None:
        """ Gets an area by name. """
        return next((area for area in self._areas.values() if area.name == name), None)

