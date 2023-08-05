from django.conf import settings


class AppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, default):
        return getattr(settings, self.prefix + name, default)

    @property
    def USERNAME_LENGTH(self):
        return self._setting('USERNAME_LENGTH', 256)

    @property
    def VIEW_LENGTH(self):
        return self._setting('VIEW_LENGTH', 256)


app_settings = AppSettings('DRF_DEBUG_')
