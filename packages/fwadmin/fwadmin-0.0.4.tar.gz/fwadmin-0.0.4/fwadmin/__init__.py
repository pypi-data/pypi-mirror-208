"""Main class."""
__author__ = "Andrea Dainese"
__contact__ = "andrea@adainese.it"
__copyright__ = "Copyright 2022, Andrea Dainese"
__license__ = "GPLv3"

from django.conf import settings

from extras.plugins import PluginConfig


PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("fwadmin", {})


class FWAdminConfig(PluginConfig):
    """Configuration class."""

    name = "fwadmin"
    verbose_name = "FWAdmin"
    description = "Firewall manager and viewer plugin for Netbox"
    version = "0.0.4"
    author = "Andrea Dainese"
    author_email = "andrea@adainese.it"
    base_url = "fwadmin"
    default_settings = {
        "EDL_UPDATE_INTERVAL": 300,
    }


config = FWAdminConfig  # pylint: disable=invalid-name
