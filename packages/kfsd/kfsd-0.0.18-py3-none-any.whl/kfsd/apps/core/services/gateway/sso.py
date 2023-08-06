from rest_framework import status
from kfsd.apps.core.auth.api.gateway import APIGateway


class SSO(APIGateway):
    def __init__(self, request=None):
        APIGateway.__init__(self, request)

    def getVerifyTokensUrl(self):
        return self.constructUrl(
            ["services.gateway.host", "services.gateway.sso.verify_tokens_uri"]
        )

    def verifyTokens(self, payload):
        return self.httpPost(self.getVerifyTokensUrl(), payload, status.HTTP_200_OK)
