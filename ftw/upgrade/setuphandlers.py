from plone.base.utils import get_installer
from plone import api

def uninstall(context):
    """Remove the ftw.upgrade leftovers only if collective.ftw.upgrade
    is not installed.
    """
    installer = get_installer(context)
    if installer.is_product_installed("collective.ftw.upgrade"):
        return

    # Remove the control panel configlet
    controlpanel = api.portal.get_tool("portal_controlpanel")
    controlpanel.unregisterConfiglet("Upgrades")

    installer.install_product("collective.ftw.upgrade")
    installer.uninstall_product("ftw.upgrade")
