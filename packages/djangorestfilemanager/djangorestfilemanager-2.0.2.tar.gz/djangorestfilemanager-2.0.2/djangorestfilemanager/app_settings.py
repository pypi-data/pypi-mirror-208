from django.conf import settings
from importlib import import_module
from six import string_types

from djangorestfilemanager.serializers import DefaultFileSerializer
from djangorestfilemanager.serializers import DefaultFileViewSerializer


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, string_types)
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)


serializers = getattr(settings, 'DJANGO_REST_FILE_MANAGER_SERIALIZERS', {})

FileSerializer = import_callable(
    serializers.get('FILE_SERIALIZER', DefaultFileSerializer)
)
FileViewSerializer = import_callable(
    serializers.get('FILE_VIEW_SERIALIZER', DefaultFileViewSerializer)
)
