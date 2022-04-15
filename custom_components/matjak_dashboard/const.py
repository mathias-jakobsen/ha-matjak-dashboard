#-----------------------------------------------------------#
#       General
#-----------------------------------------------------------#

DOMAIN = "matjak_dashboard"
PACKAGE_NAME = f"custom_components.{DOMAIN}"
PLATFORMS = []


#-----------------------------------------------------------#
#       Dashboard
#-----------------------------------------------------------#

DASHBOARD_FILENAME = "custom_components/matjak_dashboard/lovelace/ui-lovelace.yaml"
DASHBOARD_URL = "matjak-dashboard"
VIEWS_PATH = "custom_components/matjak_dashboard/lovelace/views/"


#-----------------------------------------------------------#
#       Resources
#-----------------------------------------------------------#

RESOURCES_PATH = "custom_components/matjak_dashboard/resources"
RESOURCES_STATIC_PATH = "/matjak_dashboard/resources"


#-----------------------------------------------------------#
#       YAML Parser
#-----------------------------------------------------------#

PARSER_KEYWORD = "# matjak_dashboard"
PARSER_KEY_GLOBAL = "global"