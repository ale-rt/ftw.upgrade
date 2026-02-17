import zope.deferredimport

zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please import from collective.ftw.upgrade instead of ftw.upgrade "
    "and use the namespace http://namespaces.zope.org/collective.ftw.upgrade "
    "instead of http://namespaces.zope.org/ftw.upgrade.",
    UpgradeStep="collective.ftw.upgrade:UpgradeStep",
    importProfileUpgradeStep="collective.ftw.upgrade:zcml.importProfileUpgradeStep",
    upgrade_step_directory_handler="collective.ftw.upgrade:directory.zcml.upgrade_step_directory_handler",
)
