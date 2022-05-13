#-----------------------------------------------------------#
#       General
#-----------------------------------------------------------#

DOMAIN = "matjak_dashboard"
PACKAGE_NAME = f"custom_components.{DOMAIN}"
PLATFORMS = []


#-----------------------------------------------------------#
#       Dashboard
#-----------------------------------------------------------#

DASHBOARD_FILE_PATH = "custom_components/matjak_dashboard/lovelace/ui-lovelace.yaml"
DASHBOARD_URL = "matjak-dashboard"


#-----------------------------------------------------------#
#       Resources
#-----------------------------------------------------------#

RESOURCES_PATH = "custom_components/matjak_dashboard/resources"
RESOURCES_STATIC_PATH = "/matjak_dashboard/resources"


#-----------------------------------------------------------#
#       Themes
#-----------------------------------------------------------#

THEMES_FILE_PATH_SOURCE = "custom_components/matjak_dashboard/themefiles/matjak.yaml"
THEMES_FILE_PATH_DESTINATION = "matjak/"

#-----------------------------------------------------------#
#       Translations
#-----------------------------------------------------------#

TRANSLATIONS_PATH = "custom_components/matjak_dashboard/lovelace/translations"


#-----------------------------------------------------------#
#       YAML Parser
#-----------------------------------------------------------#

PARSER_KEYWORD = "# matjak_dashboard"
PARSER_KEY_GLOBAL = "mj"