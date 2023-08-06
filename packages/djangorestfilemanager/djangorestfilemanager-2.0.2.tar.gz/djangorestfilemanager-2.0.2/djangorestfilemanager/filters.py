# -*- coding: utf-8 -*-
from django_filters import rest_framework as filters
from djangorestfilemanager.models import File


class FileFilter(filters.FilterSet):
    class Meta:
        model = File
        fields = ['uuid', 'name', 'username', 'creation_date', 'last_mod_date', 'origin', 'type', 'share']
