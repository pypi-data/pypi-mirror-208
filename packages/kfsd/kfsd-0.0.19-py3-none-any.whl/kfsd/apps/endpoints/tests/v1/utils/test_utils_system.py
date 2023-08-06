from rest_framework import status
from django.urls import reverse
from unittest.mock import patch

from kfsd.apps.endpoints.tests.endpoints_test_handler import EndpointsTestHandler
from kfsd.apps.core.utils.dict import DictUtils


class SystemUtilsTestCases(EndpointsTestHandler):
    def setUp(self):
        super().setUp()

    def get(self, url, expStatus, stripCommonAttrs=True):
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, expStatus, response.data)
        return self.stripCommonAttrs(response.data) if stripCommonAttrs else response.data

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_system_checksum_str(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/system/test_utils_system_checksum_str.json')
        obsResponse = self.post(reverse("utils-system"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/system/test_utils_system_checksum_str.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_system_checksum_dict(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/system/test_utils_system_checksum_dict.json')
        obsResponse = self.post(reverse("utils-system"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/system/test_utils_system_checksum_dict.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_system_uuid(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/system/test_utils_system_uuid.json')
        obsResponse = self.post(reverse("utils-system"), postData, status.HTTP_200_OK)
        uuid = DictUtils.get_by_path(obsResponse, "output.value")
        self.assertTrue(len(uuid) == 32)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_system_secret(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/system/test_utils_system_secret.json')
        obsResponse = self.post(reverse("utils-system"), postData, status.HTTP_200_OK)
        secret = DictUtils.get_by_path(obsResponse, "output.value")
        self.assertTrue(len(secret) > 32)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_system_key(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/system/test_utils_system_key.json')
        obsResponse = self.post(reverse("utils-system"), postData, status.HTTP_200_OK)
        key = DictUtils.get_by_path(obsResponse, "output.value")
        self.assertTrue(len(key) == 10)
