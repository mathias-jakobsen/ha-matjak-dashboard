#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import MJ_UserConfig, DomainConfig
from .areas import AreaRegistry, AreaRegistryEntry
from dataclasses import dataclass
from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_FRIENDLY_NAME, ATTR_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_devices
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_registry import async_get as async_get_entities
from typing import Optional, Union


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

DEFAULT_DOMAIN_ICON = "mdi:eye"
DEFAULT_DOMAIN_ICONS = {
    "automation": "mdi:robot",
    "binary_sensor": "mdi:checkbox-blank-circle-outline",
    "button": "mdi:gesture-tap-button",
    "camera": "mdi:cctv",
    "climate": "mdi:thermostat",
    "counter": "mdi:counter",
    "cover": "mdi:window-shutter",
    "device_tracker": "mdi:radar",
    "input_boolean": "mdi:toggle-switch-outline",
    "input_button": "mdi:gesture-tap-button",
    "input_number": "mdi:ray-vertex",
    "input_select": "mdi:format-list-bulleted",
    "input_text": "mdi:form-textbox",
    "light": "mdi:lightbulb",
    "lock": "mdi:lock",
    "media_player": "mdi:cast-connected",
    "number": "mdi:ray-vertex",
    "person": "mdi:account",
    "remote": "mdi:remote",
    "scene": "mdi:palette",
    "script": "mdi:script-text",
    "select": "mdi:format-list-bulleted",
    "sensor": "mdi:eye",
    "sun": "mdi:weather-sunny",
    "switch": "mdi:power-plug",
    "timer": "mdi:timer",
    "update": "mdi:update",
    "weather": "mdi:cloud",
    "zone": "mdi:map-marker-radius"
}


#-----------------------------------------------------------#
#       DomainRegistryEntry
#-----------------------------------------------------------#

@dataclass
class DomainRegistryEntry:
    """ A class representing a domain entry. """
    icon: str
    id: str
    priority: int


#-----------------------------------------------------------#
#       EntityRegistryEntry
#-----------------------------------------------------------#

@dataclass
class EntityRegistryEntry:
    """ A class representing an entity entry. """
    domain: str
    entity_id: str
    area_id: Optional[str] = None
    device_class: Optional[str] = None
    device_id: Optional[str] = None
    entity_category: Optional[EntityCategory] = None
    icon: Optional[str] = None
    name: Optional[str] = None
    unit_of_measurement: Optional[str] = None


#-----------------------------------------------------------#
#       EntityRegistry
#-----------------------------------------------------------#

class EntityRegistry:
    """ A class representing an entity registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, areas: AreaRegistry, config: MJ_UserConfig):
        self._areas: AreaRegistry = areas
        self._config: MJ_UserConfig = config
        self._entities: dict[str, EntityRegistryEntry] = self._get_entities(hass, config)
        self._hass: HomeAssistant = hass


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for entry in self._entities.values():
            yield entry


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_entities(self, hass: HomeAssistant, config: MJ_UserConfig) -> dict[str, EntityRegistryEntry]:
        """ Gets a dictionary containing the entity entries. """
        device_registry = async_get_devices(hass).devices
        entity_registry = async_get_entities(hass).entities
        result = {}

        for state in hass.states.async_all():
            if state.entity_id in config.exclude.entities:
                continue

            new_entry = EntityRegistryEntry(
                area_id=None,
                device_class=state.attributes.get(ATTR_DEVICE_CLASS, None),
                device_id=None,
                domain=state.domain,
                entity_category=None,
                entity_id=state.entity_id,
                name=state.attributes.get(ATTR_FRIENDLY_NAME, None),
                unit_of_measurement=state.attributes.get(ATTR_UNIT_OF_MEASUREMENT, None))

            if entity := entity_registry.get(state.entity_id):
                if entity.disabled or entity.hidden:
                    continue

                if entity.device_id:
                    device = device_registry.get(entity.device_id)

                    if device.disabled:
                        continue

                    new_entry.area_id = device.area_id
                    new_entry.device_id = device.id

                if entity.area_id:
                    new_entry.area_id = entity.area_id

                if new_entry.device_class is None:
                    new_entry.device_class = entity.device_class or entity.original_device_class or ""

                if new_entry.entity_category is None:
                    new_entry.entity_category = entity.entity_category

                if new_entry.icon is None:
                    new_entry.icon = entity.icon or entity.original_icon

                if new_entry.name is None:
                    new_entry.name = entity.name or entity.original_name

                if new_entry.unit_of_measurement is None:
                    new_entry.unit_of_measurement = entity.unit_of_measurement

            result[new_entry.entity_id] = new_entry

        return result


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_area(self, area: Union[AreaRegistryEntry, str], domain: Union[str, list[str]] = None, device_class: Union[str, list[str]] = None) -> list[EntityRegistryEntry]:
        """ Gets a list of entities by one or more areas. """
        if type(area) == str:
            area = self._areas.get_by_id(area) or self._areas.get_by_name(area)

        device_classes = type(device_class) == str and [device_class] or device_class
        domains = type(domain) == str and [domain] or domain
        result = []

        for entity in self._entities.values():
            if entity.area_id != area.id:
                continue

            if domains is not None and entity.domain not in domains:
                continue

            if device_classes is not None and entity.device_class not in device_class:
                continue

            result.append(entity)

        return result

    def get_by_device_class(self, domain: str, *device_classes: str) -> list[EntityRegistryEntry]:
        """ Gets a list of entities by one or more device classes. """
        return [entity for entity in self._entities.values() if entity.domain == domain and entity.device_class in device_classes]

    def get_by_domain(self, *domains: str) -> list[EntityRegistryEntry]:
        """ Gets a list of entity by one or more domains. """
        return [entity for entity in self._entities.values() if entity.domain in domains]

    def get_by_id(self, id: str) -> Union[EntityRegistryEntry, None]:
        """ Gets an entity by id. """
        return self._entities.get(id, None)

    def get_domains(self) -> set[str]:
        """ Gets a list of domains. """
        result: list[DomainRegistryEntry] = []

        for domain in set([entity.domain for entity in self._entities.values()]):
            domain_config = self._config.domains.get(domain, DomainConfig())
            new_entry = DomainRegistryEntry(
                icon=domain_config.icon or DEFAULT_DOMAIN_ICONS.get(domain, DEFAULT_DOMAIN_ICON),
                id=domain,
                priority=domain_config.priority
            )

            result.append(new_entry)

        return list(sorted(result, key=lambda x: (-x.priority, x.id)))
