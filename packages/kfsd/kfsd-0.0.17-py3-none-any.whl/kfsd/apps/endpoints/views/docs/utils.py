from kfsd.apps.endpoints.serializers.base import ErrorSerializer
from kfsd.apps.endpoints.views.docs.v1.utils import UtilsV1Doc
from kfsd.apps.endpoints.serializers.utils.arr import ArrUtilsInputReqSerializer, ArrUtilsOutputRespSerializer
from kfsd.apps.endpoints.serializers.utils.system import SystemInputReqSerializer, SystemOutputRespSerializer
from kfsd.apps.endpoints.serializers.utils.attr import AttrUtilsInputReqSerializer, AttrUtilsOutputRespSerializer


class UtilsDoc:
    @staticmethod
    def arr_view():
        return {
            "summary": "Array",
            "tags": ["UTILS"],
            "request": ArrUtilsInputReqSerializer,
            "responses": {
                200: ArrUtilsOutputRespSerializer,
                500: ErrorSerializer
            },
            "examples": UtilsV1Doc.arr_examples()
        }

    @staticmethod
    def system_view():
        return {
            "summary": "System",
            "tags": ["UTILS"],
            "request": SystemInputReqSerializer,
            "responses": {
                200: SystemOutputRespSerializer,
                500: ErrorSerializer
            },
            "examples": UtilsV1Doc.system_examples()
        }

    @staticmethod
    def attr_view():
        return {
            "summary": "Attr",
            "tags": ["UTILS"],
            "request": AttrUtilsInputReqSerializer,
            "responses": {
                200: AttrUtilsOutputRespSerializer,
                500: ErrorSerializer
            },
            "examples": UtilsV1Doc.attr_examples()
        }
