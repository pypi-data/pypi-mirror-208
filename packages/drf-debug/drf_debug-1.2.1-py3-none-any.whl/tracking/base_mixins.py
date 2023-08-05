from traceback import format_exc
import logging
from copy import deepcopy

from django.utils.timezone import now


logger = logging.getLogger(__name__)


class BaseLoggingMixin:
    logging_methods = '__all__'
    sensitive_fields = [
        'api',
        'token',
        'key',
        'secret',
        'password',
        'signature',
    ]

    def initial(self, request, *args, **kwargs):
        self.raise_error = False
        try:
            self.save_request_side_log(request)
        except Exception:
            self.raise_error = True
            logger.exception('Logging API call raise exception!')
        super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if self.raise_error:
            return response
        try:
            self.save_response_side_log(response)
            self.handle_log(request, response)
        except Exception:
            logger.exception('Logging API call raise exception!')
        return response

    def handle_log(self, request, response):
        raise NotImplementedError

    def should_log(self, request, response):
        return bool(
            self.logging_methods == '__all__' or
            request.method in self.logging_methods
        )

    def save_request_side_log(self, request):
        user, username = self._get_user(request)
        query_params = deepcopy(request.query_params.dict())
        self.log = {
            'requested_at': now(),
            'method': request.method,
            'host': request.get_host(),
            'path': request.path,
            'remote_addr': self._get_ip_address(request),
            'view': self._get_view_name(request),
            'view_method': self._get_view_method(request),
            'query_params': self._cleaned_data(query_params),
            'user': user,
            'username_persistent': username,
            'data': request.data,
        }

    def save_response_side_log(self, response):
        data = deepcopy(response.data)
        self.log.update({
            'response_ms': self._get_response_ms(),
            'status_code': response.status_code,
            'response': self._cleaned_data(data),
        })

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        self.log['errors'] = format_exc()
        return response

    def _get_ip_address(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '').split(',')[0]

    def _get_view_name(self, request):
        class_ = self.__class__
        return f"{class_.__module__}.{class_.__name__}"

    def _get_view_method(self, request):
        if hasattr(self, 'action'):
            return self.action or None
        return request.method.lower()

    def _get_user(self, request):
        user = request.user
        if user.is_anonymous:
            return None, 'Anonymous'
        return user, user.get_username()

    def _get_response_ms(self):
        timedelta = now() - self.log['requested_at']
        response_ms = round(timedelta.total_seconds() * 1000)
        return max(response_ms, 0)

    def _cleaned_data(self, data):
        if isinstance(data, list):
            data = [
                self._cleaned_data(item)
                for item in data
            ]
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    data[key] = self._cleaned_data(value)
                if key.lower() in self.sensitive_fields:
                    data[key] = "*************"
        return data
