from qgis.core import QgsApplication, QgsProcessingProvider
from .universal_algorithm import UniversalJoinAlgorithm

class UniversalPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initProcessing(self):
        self.provider = UniversalProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

class UniversalProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(UniversalJoinAlgorithm())
        
    def id(self): 
        return 'universal_tools'
        
    def name(self): 
        return 'Universal Tools'
        
    def icon(self): 
        return QgsProcessingProvider.icon(self)
