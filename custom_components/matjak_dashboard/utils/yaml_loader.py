#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from . import registry
from .const import (
    PARSER_KEYWORD,
)
from collections import OrderedDict
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import loader
from logging import getLogger
from typing import Callable, Dict
import io
import jinja2
import os


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__package__)


#-----------------------------------------------------------#
#       Public Functions
#-----------------------------------------------------------#

def setup_yaml_loader(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Sets up the modified YAML loader. """
    loader.load_yaml = _get_yaml_loader(hass, config_entry)

    for key, value in _get_yaml_constructors(loader.load_yaml).items():
        loader.SafeLineLoader.add_constructor(key, value)


#-----------------------------------------------------------#
#       Private Functions
#-----------------------------------------------------------#

def _get_yaml_constructors(load_yaml: Callable) -> Dict[str, Callable]:
    """ Gets a dictionary of all YAML constructors. """
    def include_yaml(ldr, node):
        args = {}
        if isinstance(node.value, str):
            fn = node.value
        else:
            fn, args, *_ = ldr.construct_sequence(node)
        filename = os.path.abspath(os.path.join(os.path.dirname(ldr.name), fn))
        try:
            return loader._add_reference(
                load_yaml(filename, ldr.secrets, args=args), ldr, node
            )
        except FileNotFoundError as exc:
            LOGGER.error("Unable to include file %s: %s", filename, exc)
            raise HomeAssistantError(exc)

    return {
        "!include": include_yaml
    }

def _get_yaml_loader(hass: HomeAssistant, config_entry: ConfigEntry):
    """ Gets the modified YAML loader. """
    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("/"))

    def load_yaml(filename, secrets = None, args = {}):
        try:
            is_lovelace_gen = False
            with open(filename, encoding="utf-8") as file:
                if file.readline().lower().startswith(PARSER_KEYWORD):
                    is_lovelace_gen = True

            if is_lovelace_gen:
                stream = io.StringIO(jinja.get_template(filename).render({**args, **registry.get_registry(hass, config_entry)}))
                stream.name = filename
                return loader.yaml.load(stream, Loader=lambda _stream: loader.SafeLineLoader(_stream, secrets)) or OrderedDict()
            else:
                with open(filename, encoding="utf-8") as file:
                    return loader.yaml.load(file, Loader=lambda stream: loader.SafeLineLoader(stream, secrets)) or OrderedDict()
        except loader.yaml.YAMLError as exc:
            LOGGER.error(str(exc))
            raise HomeAssistantError(exc)
        except UnicodeDecodeError as exc:
            LOGGER.error("Unable to read file %s: %s", filename, exc)
            raise HomeAssistantError(exc)

    return load_yaml
