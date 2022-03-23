#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import PARSER_KEYWORD
from .logger import LOGGER
from .registry import MatjakRegistry
from collections import OrderedDict
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import loader
from typing import Callable
import io
import jinja2


#-----------------------------------------------------------#
#       MatjakYamlLoader
#-----------------------------------------------------------#

class MatjakYamlLoader:
    """ A class representing the modified YAML loader. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self):
        self._old_loader: Callable = None


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def setup(self, registry: MatjakRegistry) -> None:
        """ Sets up the modified YAML loader. """
        if not self._old_loader:
            self._old_loader = loader.load_yaml

        LOGGER.debug("Setting up the modified YAML loader.")
        loader.load_yaml = self._get_load_yaml(registry)

    def remove(self) -> None:
        """ Removes the modified YAML loader. """
        if not self._old_loader:
            return

        LOGGER.debug("Removing the modified YAML loader.")
        loader.load_yaml = self._old_loader
        self._old_loader = None


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_load_yaml(self, registry: MatjakRegistry) -> None:
        """ Gets the YAML loader. """
        jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("/"))

        def load_yaml(filename: str, secrets: loader.Secrets = None, args: dict = {}) -> loader.JSON_TYPE:
            try:
                is_lovelace_gen = False
                with open(filename, encoding="utf-8") as file:
                    if file.readline().lower().startswith(PARSER_KEYWORD):
                        is_lovelace_gen = True

                if is_lovelace_gen:
                    stream = io.StringIO(jinja.get_template(filename).render({**args, **registry.as_dict()}))
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