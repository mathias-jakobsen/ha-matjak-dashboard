#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import DomainsConfig, MatjakUserConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry
from logging import getLogger


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

DEFAULT_DOMAIN_ICON = "mdi:eye"
DEFAULT_DOMAIN_ICONS = {
    "automation": "mdi:robot",
    "binary_sensor": "mdi:checkbox-blank-circle-outline",
    "button": "mdi:gesture-tap-button",
    "camera": "mdi:video",
    "climate": "mdi:thermostat",
    "cover": "mdi:window-shutter",
    "device_tracker": "mdi:radar",
    "input_boolean": "mdi:toggle-switch-outline",
    "input_button": "mdi:gesture-tap-button",
    "input_number": "mdi:ray-vertex",
    "input_select": "mdi:format-list-bulleted",
    "input_text": "mdi:form-textbox",
    "light": "mdi:lightbulb-group",
    "lock": "mdi:lock-open",
    "media_player": "mdi:cast-connected",
    "number": "mdi:ray-vertex",
    "person": "mdi:account",
    "remote": "mdi:remote",
    "scene": "mdi:palette",
    "script": "mdi:script",
    "select": "mdi:format-list-bulleted",
    "sensor": "mdi:eye",
    "switch": "mdi:power-plug",
    "update": "mdi:update",
    "weather": "mdi:cloud"
}

LOGGER = getLogger(__package__)


#-----------------------------------------------------------#
#       Class - Domains
#-----------------------------------------------------------#

class Domains:
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MatjakUserConfig):
        registry = set(map(lambda x: x.split(".")[0], hass.states.async_entity_ids()))

        self.config = config
        self.hass = hass
        self.registry = self._sort_registry(registry, config)


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for item in self.registry:
            yield item


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _sort_registry(self, registry: list[str], config: MatjakUserConfig) -> dict[str, DomainsConfig]:
        """ Returns a registry sorted by priority and name. """
        domains_config = config.domains
        sorted_domains = sorted(registry, key=lambda x: (-domains_config.get(x, DomainsConfig()).priority, x))

        return sorted_domains


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_domain_icon(self, domain: str) -> str:
        """ Gets the icon associated with the area. """
        domains_config = self.config.domains

        if domain not in domains_config:
            return DEFAULT_DOMAIN_ICON if domain not in DEFAULT_DOMAIN_ICONS else DEFAULT_DOMAIN_ICONS[domain]

        if domains_config[domain].icon is None:
            return DEFAULT_DOMAIN_ICON if domain not in DEFAULT_DOMAIN_ICONS else DEFAULT_DOMAIN_ICONS[domain]

        return domains_config[domain].icon