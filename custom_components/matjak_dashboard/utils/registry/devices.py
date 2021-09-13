#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .areas import Areas
from .base import BaseRegistry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry, device_registry
from typing import Any, Dict, List, Union


#-----------------------------------------------------------#
#       Class - Devices
#-----------------------------------------------------------#

class Devices(BaseRegistry[device_registry.DeviceEntry]):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], areas: Areas):
        exclude_keys = ["id", "name"]
        exclude_values = config.get("exclude", {}).get("devices", [])

        self.areas = areas
        self.config = config
        self.hass = hass
        self.registry = self._filter_registry(device_registry.async_get(hass).devices, exclude_keys, exclude_values)


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_area(self, area: Union[area_registry.AreaEntry, str]) -> List[device_registry.DeviceEntry]:
        """ Gets a list of devices from an area. """
        if type(area) == str:
            area = self.areas.get_by_id(area) or self.areas.get_by_name(area)

        if area is None:
            return []

        return [device for device in self.registry.values() if device.area_id == area.id]