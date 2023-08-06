from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from djangorestfilemanager.models import File
from django.contrib.auth.models import Permission, ContentType


@override_settings(ROOT_URLCONF='djangorestfilemanager.urls', PUB_SUB_EMIT=False)
class TestUploadFile(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.content_type = ContentType.objects.create(app_label='file', model='file')
        self.perm = Permission.objects.create(content_type=self.content_type, codename='download_file', name='Download File')
        self.superuser = User.objects.create(username='askywalker', is_superuser=True)
        self.owner = User.objects.create(username='lskywalker')
        self.not_owner = User.objects.create(username='chewe')
        self.not_owner.user_permissions.add(self.perm)
        file = ContentFile(b'content', name='plain.txt')
        self.file = File.objects.create(username=self.owner.username, file=file, name=file.name, share=False)
        self.client = APIClient()

    def tearDown(self):
        for file in File.objects.all():
            file.file.delete()

    def test_unauthenticated_user_cannot_download_file(self):
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def _set_file_as_not_shared(self):
        self.file.share = False
        self.file.permission = ''
        self.file.save()

    def _set_file_as_shared_with_fake_permission(self):
        self.file.share = True
        self.file.permission = 'fake permission'
        self.file.save()

    def _set_file_as_shared_with_right_permission(self):
        self.file.share = True
        self.file.permission = 'file.download_file'
        self.file.save()

    def _set_file_as_shared_with_empty_permission(self):
        self.file.share = True
        self.file.permission = ''
        self.file.save()

    def test_only_owner_can_download_not_shared_file(self):
        self._set_file_as_not_shared()
        self.client.force_authenticate(self.owner)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.client.force_authenticate(self.not_owner)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_superuser_can_download_not_shared_file(self):
        self._set_file_as_not_shared()
        self.client.force_authenticate(self.superuser)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_owner_can_download_its_shared_file_even_without_permissions(self):
        self._set_file_as_shared_with_fake_permission()
        self.client.force_authenticate(self.owner)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_owner_cannot_download_shared_file_without_permission(self):
        self._set_file_as_shared_with_fake_permission()
        self.client.force_authenticate(self.not_owner)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_not_owner_can_download_shared_file_with_permissions(self):
        self._set_file_as_shared_with_right_permission()
        self.client.force_authenticate(self.not_owner)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_owner_can_download_shared_file_with_empty_permissions(self):
        self._set_file_as_shared_with_empty_permission()
        self.client.force_authenticate(self.not_owner)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_superuser_can_download_shared_file_even_without_permissions(self):
        self._set_file_as_shared_with_right_permission()
        self.client.force_authenticate(self.superuser)
        response = self.client.get('/v1/files/{}/'.format(self.file.uuid))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
