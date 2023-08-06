from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, decorators, response, status

from kfsd.apps.endpoints.views.docs.common import CommonDoc
from kfsd.apps.endpoints.handlers.common.configuration import ConfigurationHandler
from kfsd.apps.endpoints.serializers.common.configuration import ConfigurationInputReqSerializer
from kfsd.apps.endpoints.renderers.kubefacetsjson import KubefacetsJSONRenderer
from kfsd.apps.endpoints.renderers.kubefacetsyaml import KubefacetsYAMLRenderer


class CommonViewSet(viewsets.ViewSet):
    lookup_field = "identifier"
    lookup_value_regex = '[^/]+'

    def parseInput(self, request, serializer):
        inputSerializer = serializer(data=request.data)
        inputSerializer.is_valid()
        return inputSerializer.data

    def getConfigurationInputData(self, request):
        return self.parseInput(request, ConfigurationInputReqSerializer)

    @extend_schema(**CommonDoc.config_view())
    @decorators.action(detail=False, methods=['post'], renderer_classes=[KubefacetsJSONRenderer, KubefacetsYAMLRenderer])
    def config(self, request):
        configHandler = ConfigurationHandler(self.getConfigurationInputData(request))
        return response.Response(configHandler.gen(), status.HTTP_200_OK)
