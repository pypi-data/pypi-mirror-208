from kfsd.apps.core.common.configuration import Configuration


class DjangoConfig:
    def __init__(self, config={}):
        self.__config = config

    def getConfig(self):
        return self.__config

    def findConfigs(self, paths):
        return Configuration.findConfigValues(
            self.getConfig(),
            paths
        )
