# DRF Debug

A package to tracking your API in django rest framework.

#

## Usage

```
pip install drf-debug
```

```python
INSTALLED_APPS = [
    ...
    'tracking',
]
```

```
python manage.py migrate
```

add `tracking.mixins.LoggingMixin` to any DRF view to create a instance of `APIRequestLog` every time the view is called.

```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from tracking.mixins import LoggingMixin

class LoggingView(LoggingMixin, APIView):
    def get(self, request):
        return Response('with logging')
```

For performance enhancement, explicitly choose methods to be logged using `logging_methods` attribute:

```python
class LoggingView(LoggingMixin, generics.CreateModelMixin, generics.GenericAPIView):
    logging_methods = ['POST', 'PUT']
    model = ...
```

Moreover, you could define your own rules by overriding `should_log` method. If `should_log` evaluates to True a log is created.

```python
class LoggingView(LoggingMixin, generics.GenericAPIView):
    def should_log(self, request, response):
        """Log only errors"""
        return response.status_code >= 400
```

You could define your own handling. For example save on an in-memory data structure store, remote logging system etc.

```python
class LoggingView(LoggingMixin, generics.GenericAPIView):
    def handle_log(self, request, response):
        cache.set('my_key', self.log, 86400)
```

Or you could omit save a request to the database. For example,

```python
class LoggingView(LoggingMixin, generics.GenericAPIView):
    def handle_log(self, request, response):
        """
        Save only very slow requests. Requests that took more than a second.
        """
        if self.log['response_ms'] > 1000:
            super(LoggingMixin, self).handle_log(request, response)
```

By default drf-debug is hiding the values of those fields `['api', 'token', 'key', 'secret', 'password', 'signature']` You can complete this list with your own list by putting the fields you want to be hidden in the `sensitive_fields` parameter of your view.

```python
class LoggingView(LoggingMixin, generics.CreateModelMixin, generics.GenericAPIView):
    sensitive_fields = ['password', 'my_secret_field']
```

## Links

Download Source Code: [Click Here](https://github.com/dori-dev/drf-debug/archive/refs/heads/master.zip)

My Github Account: [Click Here](https://github.com/dori-dev/)
