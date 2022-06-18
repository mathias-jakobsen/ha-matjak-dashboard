#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import DOMAIN
from .matjak import registry
from .utils.entity import MJ_Entity
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, CONF_UNIT_OF_MEASUREMENT, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change
from logging import getLogger
from statistics import mean
from typing import Any, Callable, Union


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable) -> bool:
    """ Called when a config entry is being setup.  """
    device_classes: list[str] = ["humidity", "illuminance", "temperature"]
    entities_dict: dict[str, dict[str, MJ_AggregationSensorEntity]] = {}

    async def async_on_registry_updated() -> None:
        LOGGER.debug("Configuring aggregation sensors.")
        area_ids = registry.area_registry.areas.keys()

        for area_id in [area_id for area_id in entities_dict.keys() if area_id not in area_ids]:
            for entity in entities_dict[area_id].values():
                await entity.async_remove()

            LOGGER.debug(f"Removing sensor from area {area_id}.")
            entities_dict.pop(area_id)

        for area_id in area_ids:
            if area_id not in entities_dict:
                entities_dict[area_id] = {}

            for device_class in device_classes:
                entities = registry.entity_registry.get_by_area(area_id, SENSOR_DOMAIN, device_class)
                entity_ids = [entity.entity_id for entity in entities]

                if len(entity_ids) == 0 and device_class in entities_dict[area_id]:
                    LOGGER.debug(f"Removing {device_class} sensor from {area_id}.")
                    await entities_dict[area_id].pop(device_class).async_remove()

                if len(entity_ids) > 0:
                    if device_class in entities_dict[area_id]:
                        LOGGER.debug(f"Updating {device_class} sensor from {area_id} with following entities: {entity_ids}")
                        await entities_dict[area_id][device_class].async_update_entities(entity_ids)
                    else:
                        LOGGER.debug(f"Creating {device_class} sensor from {area_id} with following entities: {entity_ids}")
                        entities_dict[area_id][device_class] = MJ_AggregationSensorEntity(area_id, device_class, entity_ids)
                        async_add_entities([entities_dict[area_id][device_class]])

    registry.add_registry_update_listener(async_on_registry_updated)
    await async_on_registry_updated()

    return True


#-----------------------------------------------------------#
#       MJ_AggregationSensorEntity
#-----------------------------------------------------------#

class MJ_AggregationSensorEntity(MJ_Entity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, area_id: str, device_class: str, entities: list[str]):
        self._area_id: str = area_id
        self._device_class: str = device_class
        self._entities: list[str] = entities
        self._state_listener: Callable = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        """ Gets the device class of the sensor. """
        return self._device_class

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """ Gets the attributes. """
        return { ATTR_ENTITY_ID: self._entities }

    @property
    def name(self) -> str:
        """ Gets the name. """
        return f"{registry.area_registry.get_by_id(self._area_id).name} {self._device_class.capitalize()}"

    @property
    def unit_of_measurement(self) -> Union[str, None]:
        """ Gets the unit of measurement. """
        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            return state.attributes.get(CONF_UNIT_OF_MEASUREMENT)

        return None


    #--------------------------------------------#
    #       Methods - Setup/Update/Remove
    #--------------------------------------------#

    async def async_setup(self, *args: Any) -> None:
        """ Triggered when the entity is being setup. """
        await self._async_setup()

    async def async_update_entities(self, entities: list[str]) -> None:
        """ Updates the entities being tracked. """
        self._entities = entities
        await self._async_setup()

    async def async_update_state(self) -> None:
        """ Updates the entity. """
        self.state = self._get_state()
        self.async_schedule_update_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """ Triggered when the entity is being removed. """
        if self._state_listener:
            self._state_listener()


    #--------------------------------------------#
    #       Event handlers
    #--------------------------------------------#

    async def async_on_state_change(self, *args) -> None:
        """ Triggered when the tracked entities changes state. """
        await self.async_update_state()


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    async def _async_setup(self) -> None:
        """ Sets up the entity list and listeners. """
        if self._state_listener:
            self._state_listener()

        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

    def _get_state(self) -> float:
        """ Reevalutes the state of the entity. """
        states = []

        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            if state.state == STATE_UNAVAILABLE:
                continue

            try:
                states.append(float(state.state))
            except:
                LOGGER.debug(f"State of {entity_id} is unknown, ignoring...")

        if len(states) > 0:
            return round(mean(states), 2)

        return STATE_UNKNOWN