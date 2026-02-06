from zope.deferredimport import deprecated

deprecated(
    "Please import from collective.ftw.upgrade instead of ftw.upgrade. ",
    UpgradeStep="collective.ftw.upgrade:UpgradeStep",
)
