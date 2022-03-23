#-----------------------------------------------------------#
#       Custom Component
#-----------------------------------------------------------#

DOMAIN = "matjak_dashboard"
PLATFORMS = []
REQUIREMENTS = [] #"browser_mod"


#-----------------------------------------------------------#
#       Configuration
#-----------------------------------------------------------#

CONF_CONFIG_PATH = "config_path"
CONF_LANGUAGE = "language"
CONF_SIDEPANEL_ICON = "sidepanel_icon"
CONF_SIDEPANEL_TITLE = "sidepanel_title"


#-----------------------------------------------------------#
#       Dashboard
#-----------------------------------------------------------#

DASHBOARD_FILENAME = "custom_components/matjak_dashboard/lovelace/ui-lovelace.yaml"
DASHBOARD_URL = "matjak-dashboard"


#-----------------------------------------------------------#
#       Resources
#-----------------------------------------------------------#

RESOURCES_PATH = "custom_components/matjak_dashboard/resources"
RESOURCES_STATIC_PATH = "/matjak_dashboard/resources"


#-----------------------------------------------------------#
#       Side Panel
#-----------------------------------------------------------#

DEFAULT_SIDEPANEL_ICON = "mdi:view-dashboard"
DEFAULT_SIDEPANEL_TITLE = "Matjak"


#-----------------------------------------------------------#
#       UI Language
#-----------------------------------------------------------#

AVAILABLE_LANGUAGES = ["dk", "en"]
DEFAULT_LANGUAGE = "en"
BUTTON_CARD_TEMPLATE_PATH = "custom_components/matjak_dashboard/lovelace/templates/button_card/"
TRANSLATIONS_PATH = "custom_components/matjak_dashboard/lovelace/translations/"


#-----------------------------------------------------------#
#       User Configuration
#-----------------------------------------------------------#

DEFAULT_CONFIG_PATH = "matjak_dashboard/"


#-----------------------------------------------------------#
#       YAML Parser
#-----------------------------------------------------------#

PARSER_KEYWORD = "# matjak_dashboard"
PARSER_KEY_GLOBAL = "_global"