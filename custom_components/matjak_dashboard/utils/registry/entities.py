#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import MatjakUserConfig
from .areas import Areas
from .base import BaseRegistry
from .devices import Devices
from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry, entity_registry
from typing import Any, Union


#-----------------------------------------------------------#
#       Class - Entities
#-----------------------------------------------------------#

class Entities(BaseRegistry[entity_registry.RegistryEntry]):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MatjakUserConfig, areas: Areas, devices: Devices):
        exclude_keys = ["entity_id", "name", "original_name"]
        exclude_values = config.exclude.entities

        self.areas = areas
        self.devices = devices
        self.config = config
        self.hass = hass
        self.registry = self._filter_registry(entity_registry.async_get(hass).entities, exclude_keys, exclude_values)


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_by_domain(self, entities: list[entity_registry.RegistryEntry], *domains: str) -> list[entity_registry.RegistryEntry]:
        """ Filters a list of entities by its domain. """
        return [entity for entity in entities if entity.domain in domains]


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_area(self, area: Union[area_registry.AreaEntry, str], domain: Union[str, list[str], None] = None) -> list[entity_registry.RegistryEntry]:
        """ Gets a list of entities in an area. """
        if type(area) == str:
            area = self.areas.get_by_id(area) or self.areas.get_by_name(area)

        if area is None:
            return []

        entities = [entity for entity in self.registry.values() if entity.area_id == area.id]
        devices = self.devices.get_by_area(area)

        for device in devices:
            for entity in [entity for entity in self.registry.values() if entity.device_id == device.id]:
                if entity.area_id is None:
                    entities.append(entity)

        if domain:
            entities = self._get_by_domain(entities, *([domain] if type(domain) == str else domain))

        return entities

    def get_by_device_class(self, *device_classes: str) -> list[entity_registry.RegistryEntry]:
        """ Gets a list of entities with a specific device class. """
        result = []

        for entity in self.registry.values():
            state = self.hass.states.get(entity.entity_id)
            device_class = (state and state.attributes.get(ATTR_DEVICE_CLASS, None) or None) or entity.device_class

            if device_class in device_classes:
                result.append(entity)

        return result

    def get_by_domain(self, *domains: str) -> list[entity_registry.RegistryEntry]:
        """ Gets a list of entities within one or several domains. """
        return self._get_by_domain(self.registry.values(), *domains)

    def get_entity_name(self, entity: entity_registry.RegistryEntry, prefix_to_remove: str = "") -> str:
        """ Gets the name of an entity. """
        name = entity.name or entity.original_name
        return name.replace(prefix_to_remove, "", 1)

    def get_by_state_attribute(self, attribute: str, value: Any) -> list[entity_registry.RegistryEntry]:
        """ Gets a list of entities which have an attribute with a specific value. """
        result = []

        for entity in self.registry.values():
            state = self.hass.states.get(entity.entity_id)

            if state and state.attributes.get(attribute, None) == value:
                result.append(entity)

        return result

    def get_state_attribute(self, entity: entity_registry.RegistryEntry, attribute: str) -> Any:
        """ Gets a state attribute of an entity. """
        state = self.hass.states.get(entity.entity_id)
        return state and state.attributes.get(attribute) or None