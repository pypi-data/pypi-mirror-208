from django.contrib import admin
from djangorestfilemanager.models import File


class FileAdmin(admin.ModelAdmin):
    search_fields = ['uuid', 'name', 'username', 'creation_date', 'last_mod_date']
    list_display = ['uuid', 'name', 'username', 'creation_date', 'last_mod_date', 'origin', 'type', 'permission',
                    'share']
    list_display_links = ['uuid', ]
    ordering = ['uuid', 'name', 'username', 'creation_date', 'last_mod_date', 'origin', 'type', 'permission',
                'share']
    list_filter = ['origin', 'type', 'share']


admin.site.register(File, FileAdmin)
