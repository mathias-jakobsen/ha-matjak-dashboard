#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass


#-----------------------------------------------------------#
#       MJ_UserConfig - Area Locations
#-----------------------------------------------------------#

@dataclass
class AreaLocationsConfig:
    """ A class representing the area locations configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    icon: str | None = None
    priority: int = 1



#-----------------------------------------------------------#
#       MJ_UserConfig - Area
#-----------------------------------------------------------#

@dataclass
class AreaConfig:
    """ A class representing the areas configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    icon: str | None = None
    location: str | None = None
    priority: int = 1
