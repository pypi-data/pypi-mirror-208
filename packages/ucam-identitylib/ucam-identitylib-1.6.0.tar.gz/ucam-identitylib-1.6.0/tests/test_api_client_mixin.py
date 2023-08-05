from unittest import TestCase
from urllib3_mock import Responses
from base64 import b64encode
from datetime import datetime, timedelta
from freezegun import freeze_time

from identitylib.card_client_configuration import CardClientConfiguration
from identitylib.card_client import ApiClient
from identitylib.card_client.api.v1beta1_api import V1beta1Api as CardApi


responses = Responses("requests.packages.urllib3")


class TestApiClientConfigurationMixin(TestCase):
    @responses.activate
    def test_access_token_is_fetched(self):
        """check the mixin requests an access token"""

        def token_callback(request):
            self.assertEqual(
                request.headers.get("Authorization"),
                f'Basic {b64encode(b"client_key_test:client_secret_test").decode("utf-8")}',
            )
            return 201, {}, '{"access_token": "test_access_token"}'

        # mock the response from the token endpoint
        responses.add_callback("POST", "/oauth2/v1/token", token_callback)

        # mock a successful request for the available barcodes
        def available_barcodes_callback(request):
            self.assertEqual(request.headers.get("Authorization"), "Bearer test_access_token")
            return 200, {}, '{"results": []}'

        responses.add_callback(
            "GET", "/card/v1beta1/available-barcodes", available_barcodes_callback
        )

        configuration = CardClientConfiguration("client_key_test", "client_secret_test")
        card_api_instance = CardApi(ApiClient(configuration))

        card_api_instance.v1beta1_available_barcodes_list()

    @responses.activate
    def test_refresh_access_token_fails(self):
        """check the mixin correctly raises exception when server responds 401"""

        # mock a 401 response code for the token
        responses.add("POST", "/oauth2/v1/token", status=401)

        configuration = CardClientConfiguration("client_key", "client_secret")
        card_api_instance = CardApi(ApiClient(configuration))

        with self.assertRaises(RuntimeError):
            card_api_instance.v1beta1_available_barcodes_list()

    @responses.activate
    def test_refresh_access_token_no_token(self):
        """check the mixin correctly raises exception when no access_token in response"""

        responses.add("POST", "/oauth2/v1/token", body="{}")

        configuration = CardClientConfiguration("client_key", "client_secret")
        card_api_instance = CardApi(ApiClient(configuration))

        with self.assertRaises(RuntimeError):
            card_api_instance.v1beta1_available_barcodes_list()

    @responses.activate
    def test_will_refresh_the_token(self):
        token_calls = 0

        # record requests for an access token
        def token_callback(request):
            nonlocal token_calls
            token_calls = token_calls + 1

            # respond with no 'expires_in' which means we use the default of 1 minute
            return 200, {}, '{"access_token": "new_access_token"}'

        responses.add_callback("POST", "/oauth2/v1/token", token_callback)

        # mock a successful request for the available barcodes
        responses.add("GET", "/card/v1beta1/available-barcodes", body='{"results": []}')

        configuration = CardClientConfiguration("client_key_test", "client_secret_test")
        card_api_instance = CardApi(ApiClient(configuration))

        now = datetime.now()
        with freeze_time(now) as frozen_datetime:
            card_api_instance.v1beta1_available_barcodes_list()
            # an access token should have been requested
            self.assertEqual(token_calls, 1)

            frozen_datetime.move_to(now + timedelta(seconds=60))
            card_api_instance.v1beta1_available_barcodes_list()

            # another access token should have been requested
            self.assertEqual(token_calls, 2)

            card_api_instance.v1beta1_available_barcodes_list()
            # our access token is still valid so we shouldn't have requested another
            self.assertEqual(token_calls, 2)

    @responses.activate
    def test_will_use_cached_token_until_expired(self):
        token_calls = 0

        # record requests for an access token
        def token_callback(request):
            nonlocal token_calls
            token_calls = token_calls + 1

            # respond with an 'expires_in' which indicates the token expires in 10 minutes
            return 200, {}, '{"access_token": "test_access_token", "expires_in": 600}'

        responses.add_callback("POST", "/oauth2/v1/token", token_callback)

        # mock a successful request for the available barcodes
        responses.add("GET", "/card/v1beta1/available-barcodes", body='{"results": []}')

        configuration = CardClientConfiguration("client_key_test", "client_secret_test")

        card_api_instance = CardApi(ApiClient(configuration))

        now = datetime.now()
        with freeze_time(now) as frozen_datetime:
            # first two calls should use the existing API token
            card_api_instance.v1beta1_available_barcodes_list()
            card_api_instance.v1beta1_available_barcodes_list()

            self.assertEqual(token_calls, 1)

            # travel forward in time
            frozen_datetime.move_to(now + timedelta(seconds=600))

            card_api_instance.v1beta1_available_barcodes_list()
            # a new access token should have been requested, so we now have two calls
            self.assertEqual(token_calls, 2)
