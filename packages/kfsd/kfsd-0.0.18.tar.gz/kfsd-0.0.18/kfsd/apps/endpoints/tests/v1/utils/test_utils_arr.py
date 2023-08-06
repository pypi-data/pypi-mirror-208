from rest_framework import status
from django.urls import reverse
from unittest.mock import patch

from kfsd.apps.endpoints.tests.endpoints_test_handler import EndpointsTestHandler


class ArrUtilsTestCases(EndpointsTestHandler):
    def setUp(self):
        super().setUp()

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_arr_join(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/arr/test_utils_arr_join.json')
        obsResponse = self.post(reverse("utils-arr"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/arr/test_utils_arr_join.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_arr_intersection(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/arr/test_utils_arr_intersection.json')
        obsResponse = self.post(reverse("utils-arr"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/arr/test_utils_arr_intersection.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_arr_merge(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/arr/test_utils_arr_merge.json')
        obsResponse = self.post(reverse("utils-arr"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/arr/test_utils_arr_merge.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_arr_merge_uniq(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/arr/test_utils_arr_merge_uniq.json')
        obsResponse = self.post(reverse("utils-arr"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/arr/test_utils_arr_merge_uniq.json')
        self.assertEqual(obsResponse, expResponse)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_utils_arr_match_and_merge(self, mocked):
        postData = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/requests/utils/arr/test_utils_arr_match_and_merge.json')
        obsResponse = self.post(reverse("utils-arr"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData('kfsd/apps/endpoints/tests/v1/data/responses/utils/arr/test_utils_arr_match_and_merge.json')
        self.assertEqual(list(obsResponse["output"]["value"]), expResponse["output"]["value"])
