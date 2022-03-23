#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import MatjakUserConfig
from homeassistant.core import HomeAssistant
from typing import Any, Generic, TypeVar, Union


#-----------------------------------------------------------#
#       Type Variables
#-----------------------------------------------------------#

T = TypeVar("T")


#-----------------------------------------------------------#
#       Class - Base
#-----------------------------------------------------------#

class BaseRegistry(Generic[T]):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MatjakUserConfig):
        self.config: MatjakUserConfig = config
        self.hass: HomeAssistant = hass
        self.registry: dict = {}


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for item in self.registry.values():
            yield item


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _filter_registry(self, registry: dict[str, T], exclude_keys: list[str], exclude_values: list[str]) -> dict[str, T]:
        """ Filters the registry by excluding certain items. """
        result = {}

        for entry_id, entry in registry.items():
            exclude = False

            for key in exclude_keys:
                if getattr(entry, key) in exclude_values:
                    exclude = True
                elif getattr(entry, "disabled_by", None) is not None:
                    exclude = True

            if not exclude:
                result[entry_id] = entry

        return result


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_id(self, id: str) -> Union[T, None]:
        """ Gets an entry by its ID. """
        return self.registry.get(id, None)