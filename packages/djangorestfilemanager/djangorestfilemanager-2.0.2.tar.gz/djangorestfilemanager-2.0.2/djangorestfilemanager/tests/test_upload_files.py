from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from djangorestfilemanager.models import File


@override_settings(ROOT_URLCONF='djangorestfilemanager.urls', PUB_SUB_EMIT=False)
class TestUploadFile(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.file = ContentFile(b'content', name='plain.txt')
        self.data = {
            'file': self.file,
            'name': 'test',
            'username': 'Luke SKW',
            'type': 'test'
        }
        User = get_user_model()
        self.user = User.objects.create(username='lskywalker', is_staff=True, is_superuser=True, is_active=True)

    def tearDown(self):
        for file in File.objects.all():
            file.file.delete()

    def test_upload_not_authenticated_file(self):
        file = {'file': (str(self.file.name), self.file, 'text/plain', {'Expires': '0'})}
        response = self.client.post('/v1/files/', data=self.data, file=file)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(0, File.objects.all().count())

    def test_upload_file(self):
        self.client.force_authenticate(user=self.user)
        file = {'file': (str(self.file.name), self.file, 'text/plain', {'Expires': '0'})}
        response = self.client.post('/v1/files/', data=self.data, file=file)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertIsNone(response.data.get('file', None))
        self.assertIsNotNone(response.data.get('uuid', None))
        fileqs = File.objects.all()
        self.assertEqual(1, fileqs.count())
        self.assertEqual(True, fileqs.last().share)
