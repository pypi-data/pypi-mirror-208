# -*- coding: utf-8 -*-
import datetime
import time
import uuid

from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
import os
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import default_storage
from djangorestfilemanager.settings import UPLOADS_DIR


class RestFileManagerStorage(S3Boto3Storage):

    def get_available_name(self, name, max_length=None):
        now = time.time()
        stamp = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d-%H-%M-%S-%f')
        return slugify('{}_{}'.format(name, stamp))


def get_file_system_storage():
    if getattr(settings, 'S3_STORAGE'):
        return RestFileManagerStorage()
    else:
        return default_storage


def set_storage_file_dir(instance, filename):
    return os.path.join(UPLOADS_DIR, instance.type, filename)


class File(models.Model):
    MASSIVE_FILE_TYPE = 'MFT'

    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True
    )
    file = models.FileField(
        verbose_name='File',
        storage=get_file_system_storage(),
        upload_to=set_storage_file_dir,
        blank=False,
        null=True
    )
    name = models.CharField(
        verbose_name='Name',
        max_length=255
    )
    username = models.CharField(
        'Username',
        max_length=100
    )
    creation_date = models.DateTimeField(
        verbose_name='Creation date',
        auto_now_add=True,
    )
    last_mod_date = models.DateTimeField(
        verbose_name='Creation date',
        auto_now=True,
    )
    origin = models.CharField(
        verbose_name='Origin',
        blank=True,
        null=True,
        max_length=3,
        default='API'
    )
    type = models.CharField(
        verbose_name='Type',
        blank=True,
        null=True,
        max_length=10,
        default='file',
        db_index=True,
    )
    permission = models.CharField(
        verbose_name='Permission',
        max_length=200,
        blank=True,
        null=True,
        default=''
    )
    share = models.BooleanField(
        verbose_name='Share',
        default=True
    )
    status = models.CharField(
        'Status',
        max_length=3
    )
    data = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        indexes = (
            BrinIndex(fields=('creation_date', )),
        )

    def __str__(self):
        return '{}-{}'.format(self.name, self.type)

    def to_dict(self):
        return {
            'uuid': str(self.uuid),
            'name': self.name,
            'origin': self.origin,
            'type': self.type,
            'username': self.username
        }
