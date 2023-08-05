from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class APIDocsViewTests(TestCase):
    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    def test_get(self, mocked):
        mocked.side_effect = [{}]
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
