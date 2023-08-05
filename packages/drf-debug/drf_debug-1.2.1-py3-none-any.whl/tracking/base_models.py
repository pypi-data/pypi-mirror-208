from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class BaseAPIRequestLog(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    username_persistent = models.CharField(
        max_length=getattr(settings, 'DRF_DEBUG_USERNAME_LENGTH', 256),
        null=True,
        blank=True,
    )
    requested_at = models.DateTimeField(
        db_index=True,
    )
    response_ms = models.PositiveIntegerField(
        default=0,
    )
    path = models.CharField(
        max_length=2048,
        db_index=True,
        help_text='The url path.',
    )
    view = models.CharField(
        max_length=getattr(settings, 'DRF_DEBUG_VIEW_LENGTH', 256),
        null=True,
        blank=True,
        db_index=True,
        help_text='View called by this endpoint.',
    )
    view_method = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
    )
    remote_addr = models.GenericIPAddressField()
    host = models.URLField()
    method = models.CharField(
        max_length=16,
        db_index=True,
    )
    query_params = models.JSONField(
        default=dict,
        null=True,
        blank=True,
    )
    data = models.JSONField(
        default=dict,
        null=True,
        blank=True,
    )
    response = models.JSONField(
        default=dict,
        null=True,
        blank=True,
    )
    errors = models.TextField(
        null=True,
        blank=True,
    )
    status_code = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        verbose_name = 'API Request Log'
        ordering = [
            '-requested_at',
        ]

    def __str__(self) -> str:
        return f'{self.method} {self.path}'
