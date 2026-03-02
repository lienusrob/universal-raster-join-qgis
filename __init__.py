def classFactory(iface):
    from .universal_plugin import UniversalPlugin
    return UniversalPlugin(iface)
