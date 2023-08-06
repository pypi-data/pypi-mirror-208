from kfsd.apps.core.auth.base import BaseUser
from kfsd.apps.core.auth.api.token import TokenAuth
from kfsd.apps.core.utils.dict import DictUtils


class TokenUser(BaseUser, TokenAuth):
    def __init__(self, request):
        BaseUser.__init__(self)
        TokenAuth.__init__(self, request=request)
        self.setUserInfo(self.getTokenUserInfo())

    def getUserCookies(self):
        userInfo = self.getUserInfo()
        return DictUtils.get_by_path(userInfo, "data.cookies")
