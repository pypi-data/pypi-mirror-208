from kfsd.apps.core.services.gateway.sso import SSO


class TokenAuth(SSO):
    def __init__(self, request=None):
        SSO.__init__(self, request)

    def getTokenUserInfo(self):
        payload = {
            "cookies": self.getDjangoRequest().getDjangoReqCookies().getAllCookies()
        }
        return self.verifyTokens(payload)
