# -*- coding: utf-8 -*-
from django.http import HttpResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from djangorestfilemanager.models import File
from djangorestfilemanager.filters import FileFilter
from djangorestfilemanager.permissions import FilePermissions
from djangorestfilemanager.app_settings import FileSerializer, FileViewSerializer
import logging

logger = logging.getLogger(__name__)


class FileModelViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_class = FileFilter
    search_fields = ['name', 'uuid']
    ordering_fields = ['name', 'uuid', 'username', 'origin', 'type']
    permission_classes = (FilePermissions,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FileViewSerializer
        return FileSerializer

    def perform_create(self, serializer):
        user = self.request.user
        filename = serializer.validated_data.get('file').name
        instance = serializer.save(username=user.username, name=filename)
        logger.info('- File uuid: {}, uploaded by user {}'.format(instance.uuid, user.username))

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        response = HttpResponse(obj.file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % obj.name
        logger.info('- File uuid: {}, downloaded by user {}'.format(obj.uuid, request.user.username))
        return response
