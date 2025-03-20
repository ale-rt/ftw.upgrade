from AccessControl import getSecurityManager
from AccessControl import Permissions
from ftw.upgrade.jsonapi.base import APIView
from ftw.upgrade.jsonapi.utils import action
from ftw.upgrade.jsonapi.utils import jsonify
from plone.base.interfaces import IPloneSiteRoot
from ZODB.broken import Broken


class ZopeAppAPI(APIView):

    @jsonify
    @action('GET')
    def list_plone_sites(self):
        """Returns a list of Plone sites.
        """

        return list(self._get_plone_sites())

    @jsonify
    @action('GET')
    def current_user(self):
        """Return the current user when authenticated properly.
        This can be used for testing authentication.
        """
        return getSecurityManager().getUser().getId()

    def sites(self, root=None):
        """ Copy the method in Products.CMFPlone.browser.admin.Overview.sites

        The overview_view does not have this method anymore since Plone 6.1.
        """
        if root is None:
            root = self.context

        result = []
        secman = getSecurityManager()
        candidates = (
            obj for obj in root.values() if not isinstance(obj, Broken)
        )
        for obj in candidates:
            if obj.meta_type == "Folder":
                result = result + self.sites(obj)
            elif IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(Permissions.view, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, "_mount_points", {}):
                result.extend(self.sites(root=obj))
        return result

    def _get_plone_sites(self):
        for site in self.sites():
            yield {'id': site.getId(),
                   'path': '/'.join(site.getPhysicalPath()),
                   'title': site.Title()}
