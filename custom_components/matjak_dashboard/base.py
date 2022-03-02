#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .utils.config import MatjakConfig
from .utils.logger import LOGGER
from .utils.frontend import MatjakFrontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


#-----------------------------------------------------------#
#       Matjak
#-----------------------------------------------------------#

class Matjak:
    """ A class representing the base integration functionality. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.config = MatjakConfig(**{ **config_entry.data, **config_entry.options })
        self.frontend = MatjakFrontend(hass, self.config)
        self.hass = hass