from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from tracking.mixins import LoggingMixin


class MockNoLoggingView(APIView):
    def get(self, request):
        return Response('no logging')


class MockLoggingView(LoggingMixin, APIView):
    def get(self, request):
        return Response({'secret': 'hello'}, status=200)

    def post(self, request):
        return Response({})


class MockExplicitLoggingView(LoggingMixin, APIView):
    logging_methods = [
        'POST',
    ]

    def get(self, request):
        return Response('no logging')

    def post(self, request):
        return Response('with logging')


class MockCustomCheckLoggingView(LoggingMixin, APIView):
    def should_log(self, request, response):
        return 'log' in response.data

    def get(self, request):
        return Response(['user1', 'user2', 'log'])

    def post(self, request):
        return Response(['mohammad', 'john', 'dori'])


class MockSessionAuthLoggingView(LoggingMixin, APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        SessionAuthentication,
    ]

    def get(self, request):
        return Response('session auth logging')


class MockSensitiveFieldsLoggingView(LoggingMixin, APIView):
    sensitive_fields = [
        'secret_field',
    ]

    def get(self, request):
        return Response({
            'sensitive': True,
            'secret_field': 'this is a secret',
        })
