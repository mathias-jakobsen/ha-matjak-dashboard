#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DOMAIN
from dataclasses import dataclass, field
from typing import ClassVar
import voluptuous as vol


#-----------------------------------------------------------#
#       MatjakConfig
#-----------------------------------------------------------#

@dataclass
class MJ_Config:
    """ A class representing the ConfigFlow options. """

    #--------------------------------------------#
    #       Constants
    #--------------------------------------------#

    LANGUAGES: ClassVar[list[str]] = ["en", "dk"]


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    language: str = field(default=LANGUAGES[0])
    sidepanel_icon: str = "mdi:view-dashboard"
    sidepanel_title: str = "Matjak Dashboard"
    themes_path: str = "themes/"
    user_config_path: str = f"{DOMAIN}/"


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def get_schema(self) -> vol.Schema:
        """ Gets the voluptuous schema. """
        return vol.Schema({
            vol.Required("sidepanel_title", default=self.sidepanel_title): str,
            vol.Required("sidepanel_icon", default=self.sidepanel_icon): str,
            vol.Required("language", default=self.language): vol.In(self.LANGUAGES),
            vol.Required("themes_path", default=self.themes_path): str,
            vol.Required("user_config_path", default=self.user_config_path): str
        })

