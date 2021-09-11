# -----------------------------------------------------------#
#       Imports
# -----------------------------------------------------------#

from .const import (
    RESOURCES_PATH,
    RESOURCES_STATIC_PATH
)
from homeassistant.core import HomeAssistant
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.util.yaml import loader
from logging import getLogger


# -----------------------------------------------------------#
#       Constants
# -----------------------------------------------------------#

LOGGER = getLogger(__name__)


# -----------------------------------------------------------#
#       Functions
# -----------------------------------------------------------#

async def async_create_resources(hass: HomeAssistant) -> None:
    """ Creates the resources found in the resources directory. """
    plugin_path = hass.config.path(RESOURCES_PATH)
    resources: ResourceStorageCollection = hass.data['lovelace']['resources']

    hass.http.register_static_path(RESOURCES_STATIC_PATH, plugin_path, True)

    for filename in loader._find_files(plugin_path, "*.js"):
        resource_url = filename.replace(plugin_path, RESOURCES_STATIC_PATH)

        for item in resources.async_items():
            if item["url"].startswith(resource_url):
                break

            if isinstance(resources, ResourceStorageCollection):
                await resources.async_create_item({"res_type": "module", "url": resource_url})
            else:
                add_extra_js_url(hass, resource_url)

async def async_remove_resources(hass: HomeAssistant) -> None:
    """ Removes the resources. """
    resources: ResourceStorageCollection = hass.data['lovelace']['resources']

    for item in resources.async_items():
        if not item["url"].startswith(RESOURCES_STATIC_PATH):
            continue

        await resources.async_delete_item(item["id"])