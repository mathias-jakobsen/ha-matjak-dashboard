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
class MatjakConfig:
    """ A class representing the ConfigFlow options. """

    #--------------------------------------------#
    #       Constants
    #--------------------------------------------#

    LANGUAGES: ClassVar[list[str]] = ["en", "dk"]


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    config_path: str = f"{DOMAIN}/"
    language: str = field(default=LANGUAGES[0])
    sidepanel_icon: str = "mdi:view-dashboard"
    sidepanel_title: str = "Matjak Dashboard"


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def get_schema(self) -> vol.Schema:
        """ Gets the voluptuous schema. """
        return vol.Schema({
            vol.Required("sidepanel_title", default=self.sidepanel_title): str,
            vol.Required("sidepanel_icon", default=self.sidepanel_icon): str,
            vol.Required("language", default=self.language): vol.In(self.LANGUAGES),
            vol.Required("config_path", default=self.config_path): str
        })
