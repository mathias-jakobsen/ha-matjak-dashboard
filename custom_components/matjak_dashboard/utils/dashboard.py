# -----------------------------------------------------------#
#       Imports
# -----------------------------------------------------------#

from .const import (
    CONF_SIDEPANEL_ICON,
    CONF_SIDEPANEL_TITLE,
    DASHBOARD_FILENAME,
    DASHBOARD_URL
)
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.lovelace.dashboard import LovelaceYAML
from homeassistant.components.lovelace import _register_panel
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


# -----------------------------------------------------------#
#       Functions
# -----------------------------------------------------------#

def create_dashboard(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Creates the dashboard. """
    sidepanel_icon = config_entry.options.get(CONF_SIDEPANEL_ICON, config_entry.data.get(CONF_SIDEPANEL_ICON))
    sidepanel_title = config_entry.options.get(CONF_SIDEPANEL_TITLE, config_entry.data.get(CONF_SIDEPANEL_TITLE))

    dashboard_config = {
        "mode": "yaml",
        "icon": sidepanel_icon,
        "title": sidepanel_title,
        "filename": DASHBOARD_FILENAME,
        "show_in_sidebar": True,
        "require_admin": False
    }

    hass.data["lovelace"]["dashboards"][DASHBOARD_URL] = LovelaceYAML(hass, DASHBOARD_URL, dashboard_config)
    _register_panel(hass, DASHBOARD_URL, "yaml", dashboard_config, False)

def remove_dashboard(hass: HomeAssistant) -> None:
    """ Removes the dashboard. """
    async_remove_panel(hass, DASHBOARD_URL)
    hass.data["lovelace"]["dashboards"].pop(DASHBOARD_URL)