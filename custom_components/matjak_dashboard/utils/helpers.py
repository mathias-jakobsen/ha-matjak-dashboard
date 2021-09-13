#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import (
    BUTTON_CARD_TEMPLATE_PATH,
    TRANSLATIONS_PATH
)
from collections import OrderedDict
from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import loader
from typing import Dict
import os


#-----------------------------------------------------------#
#       Functions
#-----------------------------------------------------------#

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