from tracking.base_mixins import BaseLoggingMixin

from tracking.models import APIRequestLog


class LoggingMixin(BaseLoggingMixin):
    def handle_log(self, request, response):
        if self.should_log(request, response):
            APIRequestLog(**self.log).save()
