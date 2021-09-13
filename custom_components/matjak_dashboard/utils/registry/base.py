#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.core import HomeAssistant
from typing import Any, Dict, Generic, List, TypeVar, Union


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

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        self.registry = {}


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for item in self.registry.values():
            yield item


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _filter_registry(self, registry: Dict[str, T], exclude_keys: List[str], exclude_values: List[str]) -> Dict[str, T]:
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