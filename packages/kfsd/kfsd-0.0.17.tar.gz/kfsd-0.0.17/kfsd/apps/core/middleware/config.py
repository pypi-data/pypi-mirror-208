from django.conf import settings
from kfsd.apps.core.utils.dict import DictUtils
from kfsd.apps.core.utils.system import System
from kfsd.apps.core.common.configuration import Configuration


class KubefacetsConfigMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.__config = self.genConfig()

    def genConfig(self):
        return self.deriveConfig()

    def deriveConfig(self):
        kubefacetsSettings = settings.KUBEFACETS
        isLocalConfig = DictUtils.get_by_path(kubefacetsSettings, "config.is_local_config")
        lookupDimensions = DictUtils.get_by_path(kubefacetsSettings, "config.lookup_dimension_keys")
        if isLocalConfig:
            localConfig = DictUtils.get_by_path(kubefacetsSettings, "config.local")
            return self.genLocalConfig(lookupDimensions, localConfig)
        return None

    def genLocalConfig(self, dimensionKeys, config):
        dimensions = self.constructDimensionsFromEnv(dimensionKeys)
        return Configuration(settings=config, dimensions=dimensions)

    def constructDimensionsFromEnv(self, dimensionKeys):
        return {key: System.getEnv(key) for key in dimensionKeys}

    def __call__(self, request):
        request.config = self.__config
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None
