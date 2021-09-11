# -----------------------------------------------------------#
#       Imports
# -----------------------------------------------------------#

from .const import (
    CONF_CONFIG_PATH,
    PARSER_KEYWORD,
    PARSER_KEY_BUTTON_CARD_TEMPLATE_LIST,
    PARSER_KEY_CONFIG,
    PARSER_KEY_GLOBAL,
    PARSER_KEY_REGISTRY,
    PARSER_KEY_TRANSLATIONS
)
from .user_config import USER_CONFIG_SCHEMA
from collections import OrderedDict
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import loader
from logging import getLogger
from typing import Any, Callable, Dict
import io
import jinja2
import os


# -----------------------------------------------------------#
#       Constants
# -----------------------------------------------------------#

LOGGER = getLogger(__package__)


# -----------------------------------------------------------#
#       Public Functions
# -----------------------------------------------------------#

def setup_yaml_loader(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Sets up the modified YAML loader. """
    loader.load_yaml = _get_yaml_loader(hass, config_entry)

    for key, value in _get_yaml_constructors(loader.load_yaml).items():
        loader.SafeLineLoader.add_constructor(key, value)


# -----------------------------------------------------------#
#       Private Functions
# -----------------------------------------------------------#

def _load_user_config(hass: HomeAssistant, config_entry: ConfigEntry, load_yaml: Callable) -> Dict[str, Any]:
    """ Loads the user configuration from the configuration directory. """
    result = {}
    config_path = config_entry.options.get(CONF_CONFIG_PATH, config_entry.data.get(CONF_CONFIG_PATH))
    path = hass.config.path(config_path)
    LOGGER.error("helllo wolrd")
    if os.path.exists(path):
        dashboard_config = {}

        for filename in loader._find_files(path, "*.yaml"):
            config = load_yaml(filename)

            if isinstance(config, dict):
                dashboard_config.update(config)

        result.update(dashboard_config)

    return USER_CONFIG_SCHEMA(result)

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
                config = _load_user_config(hass, config_entry, load_yaml)
                stream = io.StringIO(jinja.get_template(filename).render({
                            **args,
                            PARSER_KEY_GLOBAL: {
                                PARSER_KEY_CONFIG: config,
                                #PARSER_KEY_REGISTRY: get_registry(hass, logger, config),
                                #PARSER_KEY_BUTTON_CARD_TEMPLATE_LIST: get_button_card_template_list(hass),
                                #PARSER_KEY_TRANSLATIONS: get_translations(hass, config_entry)
                            }
                        }))
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
