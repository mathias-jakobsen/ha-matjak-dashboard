#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import (
    DASHBOARD_FILENAME,
    DASHBOARD_URL,
    RESOURCES_PATH,
    RESOURCES_STATIC_PATH
)
from .config import MatjakConfig
from .logger import LOGGER
from homeassistant.components.frontend import add_extra_js_url, async_remove_panel
from homeassistant.components.lovelace import _register_panel
from homeassistant.components.lovelace.dashboard import LovelaceYAML
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import loader


#-----------------------------------------------------------#
#       MatjakFrontend
#-----------------------------------------------------------#

class MatjakFrontend:
    """ A class that handles the frontend setup. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MatjakConfig):
        self.config = config
        self.hass = hass

        LOGGER.debug(f"Setting up static path {RESOURCES_STATIC_PATH}.")
        hass.http.register_static_path(RESOURCES_STATIC_PATH, hass.config.path(RESOURCES_PATH), True)


    #--------------------------------------------#
    #       Methods: Dashboard
    #--------------------------------------------#

    async def async_create_dashboard(self) -> None:
        """ Creates the dashboard. """
        LOGGER.debug(f"Setting up the dashboard (url={DASHBOARD_URL}).")

        dashboard_config = {
            "mode": "yaml",
            "icon": self.config.sidepanel_icon,
            "title": self.config.sidepanel_title,
            "filename": DASHBOARD_FILENAME,
            "show_in_sidebar": True,
            "require_admin": False
        }

        self.hass.data["lovelace"]["dashboards"][DASHBOARD_URL] = LovelaceYAML(self.hass, DASHBOARD_URL, dashboard_config)
        _register_panel(self.hass, DASHBOARD_URL, "yaml", dashboard_config, False)

    async def async_remove_dashboard(self) -> None:
        """ Removes the dashboard. """
        LOGGER.debug(f"Removing dashboard (url={DASHBOARD_URL}).")
        async_remove_panel(self.hass, DASHBOARD_URL)
        self.hass.data["lovelace"]["dashboards"].pop(DASHBOARD_URL)


    #--------------------------------------------#
    #       Methods: Resources
    #--------------------------------------------#

    async def async_setup_resources(self) -> None:
        """ Sets up the custom lovelace resources. """
        resources: ResourceStorageCollection = self.hass.data["lovelace"]["resources"]
        resources_path = self.hass.config.path(RESOURCES_PATH)

        for filename in loader._find_files(resources_path, "*.js"):
            resource_url = filename.replace(resources_path, RESOURCES_STATIC_PATH)
            skip = False

            for item in resources.async_items():
                url: str = item["url"]

                if url.startswith(resource_url):
                    skip = True
                    break

            if skip:
                continue

            LOGGER.debug(f"Adding resource {resource_url.replace(RESOURCES_STATIC_PATH, '')}.")

            if isinstance(resources, ResourceStorageCollection):
                await resources.async_create_item({"res_type": "module", "url": resource_url})
            else:
                add_extra_js_url(self.hass, resource_url)

    async def async_remove_resources(self) -> None:
        """ Removes the custom lovelace resources. """
        resources: ResourceStorageCollection = self.hass.data["lovelace"]["resources"]

        if not isinstance(resources, ResourceStorageCollection):
            LOGGER.warning(f"Cannot remove resources: Lovelace mode is set to YAML. Restart Homeassistant to remove the resources.")
            return

        for item in resources.async_items():
            url: str = item["url"]

            if not url.startswith(RESOURCES_STATIC_PATH):
                continue

            LOGGER.debug(f"Removing {url.replace(RESOURCES_STATIC_PATH, '')} from the resource collection.")
            await resources.async_delete_item(item["id"])

