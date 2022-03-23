#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import (
    BUTTON_CARD_TEMPLATE_PATH,
    TRANSLATIONS_PATH
)
from collections import OrderedDict
from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.util.yaml import loader
from typing import Callable, Dict, List
import os


#-----------------------------------------------------------#
#       Functions
#-----------------------------------------------------------#

def get_button_card_template(hass: HomeAssistant, button_card_template_list: List[str]) -> Callable[[entity_registry.RegistryEntry, str], str]:
    """ Gets a button card template for an entity. """
    def get(entity: entity_registry.RegistryEntry, default: str = "base_button") -> str:
        if entity.domain == "sensor" or entity.domain == "binary_sensor":
            state = hass.states.get(entity.entity_id)
            device_class = state and state.attributes.get(ATTR_DEVICE_CLASS, entity.device_class) or entity.device_class
            template = f"{entity.domain}_{device_class}_button"

            return template if template in button_card_template_list else default

        template = f"{entity.domain}_button"
        return template if template in button_card_template_list else default

    return get

def get_button_card_template_list(hass: HomeAssistant) -> bool:
    """ Gets a list of available button card templates. """
    result = []
    path = hass.config.path(BUTTON_CARD_TEMPLATE_PATH)

    for filename in loader._find_files(path, "*.yaml"):
        result.append(os.path.splitext(filename)[0].split("/")[-1])

    return result

def get_translations(hass: HomeAssistant, language: str) -> Dict[str, str]:
    """ Gets a dictionary of translation strings. """
    filename = hass.config.path(f"{TRANSLATIONS_PATH}{language}.yaml")

    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as file:
            return loader.yaml.load(file, Loader=lambda stream: loader.SafeLineLoader(stream, None)) or OrderedDict()

    return {}