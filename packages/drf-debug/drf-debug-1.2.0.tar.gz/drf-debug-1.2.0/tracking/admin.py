from django.contrib import admin

from tracking.models import APIRequestLog


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'requested_at'
    list_display = [
        'id',
        'requested_at',
        'response_ms',
        'status_code',
        'user',
        'view_method',
        'path',
        'remote_addr',
        'host',
        'query_params',
    ]
    list_filter = [
        'view_method',
        'status_code',
    ]
    search_fields = [
        'path',
        'user__username',
    ]
    raw_id_fields = [
        'user',
    ]
