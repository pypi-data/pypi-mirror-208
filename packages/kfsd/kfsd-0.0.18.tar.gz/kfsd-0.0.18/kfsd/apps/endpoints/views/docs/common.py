from kfsd.apps.endpoints.serializers.base import ErrorSerializer
from kfsd.apps.endpoints.views.docs.v1.common import CommonV1Doc
from kfsd.apps.endpoints.serializers.common.configuration import ConfigurationInputReqSerializer, ConfigurationOutputRespSerializer


class CommonDoc:
    @staticmethod
    def config_view():
        return {
            "summary": "Config",
            "tags": ["COMMON"],
            "request": ConfigurationInputReqSerializer,
            "responses": {
                200: ConfigurationOutputRespSerializer,
                500: ErrorSerializer
            },
            "examples": CommonV1Doc.config_examples()
        }
