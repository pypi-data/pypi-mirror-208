from kfsd.apps.core.utils.http.django.cookie import Cookie
from kfsd.apps.core.utils.http.django.config import DjangoConfig


class DjangoRequest(DjangoConfig):
    def __init__(self, request=None):
        self.__request = request
        self.__djangoCookies = Cookie(request)
        DjangoConfig.__init__(self, self.getConfigData())

    def getRequest(self):
        return self.__request

    def getDjangoReqCookies(self):
        return self.__djangoCookies

    def getConfigData(self):
        return self.__request.config.getFinalConfig()

    def parseInputData(self, serializer, raiseExceptions=True):
        inputSerializer = serializer(data=self.__request.data)
        inputSerializer.is_valid(raise_exception=raiseExceptions)
        return inputSerializer.data
