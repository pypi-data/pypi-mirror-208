from rest_framework import status
from django.urls import reverse
from unittest.mock import patch

from kfsd.apps.endpoints.tests.endpoints_test_handler import EndpointsTestHandler


class ConfigurationTestCases(EndpointsTestHandler):
    def setUp(self):
        super().setUp()

    def postYaml(self, url, data, expStatus,):
        response = self.client.post(url, data, format='yaml')
        self.assertEqual(response.status_code, expStatus)
        print(response)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_common_config_dev(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/common/config/test_common_config_dev.json')
        obsResponse = self.post(reverse("common-config"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/common/config/test_common_config_dev.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_common_config_prod(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/common/config/test_common_config_prod.json')
        obsResponse = self.post(reverse("common-config"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/common/config/test_common_config_prod.json')
        self.assertEqual(obsResponse, expResponse)
