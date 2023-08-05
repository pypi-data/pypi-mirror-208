import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory
from django.test import override_settings

from tracking.models import APIRequestLog
from .views import MockLoggingView


@override_settings(ROOT_URLCONF='tracking.tests.urls')
class TestLoggingMixin(APITestCase):
    def test_no_logging_no_log_created(self):
        self.client.get('/no-logging/')
        self.assertEqual(APIRequestLog.objects.count(), 0)

    def test_logging_creates_log(self):
        self.client.get('/logging/')
        self.assertEqual(APIRequestLog.objects.count(), 1)

    def test_log_path(self):
        self.client.get('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.path, '/logging/')

    def test_log_remote_ip(self):
        request = APIRequestFactory().get('/logging/')
        request.META['REMOTE_ADDR'] = '127.0.0.2'
        MockLoggingView.as_view()(request).render()
        log = APIRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.0.2')

    def test_log_remote_ipv6(self):
        request = APIRequestFactory().get('/logging/')
        ip = '2001:0db8:3444:2222::ae24:0245:'
        request.META['REMOTE_ADDR'] = ip
        MockLoggingView.as_view()(request).render()
        log = APIRequestLog.objects.first()
        self.assertEqual(log.remote_addr, ip)

    def test_log_remote_ipv6_loopback(self):
        request = APIRequestFactory().get('/logging/')
        request.META['REMOTE_ADDR'] = '::1'
        MockLoggingView.as_view()(request).render()
        log = APIRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '::1')

    def test_log_remote_ip_list(self):
        request = APIRequestFactory().get('/logging/')
        request.META['REMOTE_ADDR'] = '127.0.1.2, 127.0.0.3, 121.1.1.1'
        MockLoggingView.as_view()(request).render()
        log = APIRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.1.2')

    def test_log_ip_x_forwarded_for(self):
        request = APIRequestFactory().get('/logging/')
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.1.2, 127.0.0.3, 121.1.1.1'
        MockLoggingView.as_view()(request).render()
        log = APIRequestLog.objects.first()
        self.assertEqual(log.remote_addr, '127.0.1.2')

    def test_log_host(self):
        self.client.get('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.host, 'testserver')

    def test_log_method_GET(self):
        self.client.get('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.method, 'GET')

    def test_log_method_POST(self):
        self.client.post('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.method, 'POST')

    def test_log_status_code(self):
        self.client.get('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.status_code, 200)

    def test_logging_explicit(self):
        self.client.get('/explicit-logging/')
        self.client.post('/explicit-logging/')
        self.assertEqual(APIRequestLog.objects.count(), 1)
        obj = APIRequestLog.objects.first()
        self.assertEqual(obj.response, 'with logging')
        self.assertEqual(obj.method, 'POST')

    def test_custom_check_logging(self):
        self.client.get('/custom-check-logging/')
        self.client.post('/custom-check-logging/')
        self.assertEqual(APIRequestLog.objects.count(), 1)
        obj = APIRequestLog.objects.first()
        self.assertEqual(obj.method, 'GET')
        self.assertIn('log', obj.response)

    def test_log_anon_user(self):
        self.client.get('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.user, None)
        self.assertEqual(log.username_persistent, 'Anonymous')

    def test_session_auth_logging(self):
        user_data = {
            'username': 'testuser',
            'password': '1234',
        }
        user = get_user_model().objects.create_user(**user_data)
        self.client.login(**user_data)
        self.client.get('/logging/')
        log = APIRequestLog.objects.first()
        self.assertEqual(log.user, user)
        self.assertEqual(log.username_persistent, user_data['username'])

    def test_params_logging(self):
        self.client.get('/logging/?a=b&ok=1')
        log = APIRequestLog.objects.first()
        self.assertEqual(
            log.query_params,
            {'a': 'b', 'ok': '1'},
        )

    def test_sensitive_params_logging(self):
        query = '?name=mohammad&secret_field=1234'
        self.client.get(f'/sensitive-fields-logging/{query}')
        log = APIRequestLog.objects.first()
        self.assertIn('secret_field', log.query_params)
        self.assertNotEqual(log.query_params['secret_field'], '1234')
        self.assertEqual(log.query_params, {
            'name': 'mohammad',
            'secret_field': '*************',
        })

    @mock.patch.object(
        APIRequestLog,
        'save',
        side_effect=Exception('DB Failure')
    )
    def test_log_does_not_prevent_api_call_if_log_save_fails(self, mock_save):
        response = self.client.get('/logging/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(APIRequestLog.objects.count(), 0)

    @override_settings(USE_TZ=False)
    @mock.patch('tracking.base_mixins.now')
    def test_log_does_not_fail_with_negative_response_ms(self, mock_now):
        mock_now.side_effect = [
            datetime.datetime(2023, 1, 1, 10, 2, 10),
            datetime.datetime(2023, 1, 1, 10, 2, 5),
        ]
        response = self.client.get('/logging/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(APIRequestLog.objects.count(), 1)
        log = APIRequestLog.objects.first()
        self.assertEqual(log.response_ms, 0)
