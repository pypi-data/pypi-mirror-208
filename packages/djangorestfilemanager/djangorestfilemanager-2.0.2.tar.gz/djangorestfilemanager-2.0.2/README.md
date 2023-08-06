# Django REST File Manager

A package that provides authenticated file management (upload/download) using REST Framework and Amazon S3 (optionally)

Install app:

````bash
pip install djangorestfilemanager
````

Add in installed apps:

````python
INSTALLED_APPS = [..., 'rest_framework', 'django_filters', 'djangorestfilemanager.apps.DjangoRestFileManagerConfig']

````

/proyect/settings.py

Specific app settings, by default will save in /files/.... 
````python
REST_FILE_MANAGER = {
    'UPLOADS_DIR': '...'
}
````

S3 storage setup. 

If AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME is not provided, files will save in local storage
```python
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media', 'files')

S3_STORAGE = False
AWS_DEFAULT_ACL = None

if env('AWS_ACCESS_KEY_ID') and env('AWS_SECRET_ACCESS_KEY') and env(
        'AWS_STORAGE_BUCKET_NAME'):
    S3_STORAGE = True
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_LOCATION = 'media'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_ENCRYPTION = True
    AWS_IS_GZIPPED = True
    GZIP_CONTENT_TYPES = (
        'application/pdf', 'application/json', 'text/csv', 'application/xml', 'application/xhtml+xml',
        'application/msword', 'application/vnd.oasis.opendocument.presentation',
        'application/vnd.oasis.opendocument.spreadsheet', 'application/vnd.oasis.opendocument.text',
        'application/vnd.ms-powerpoint', 'application/x-rar-compressed', 'application/xhtml+xml',
        'application/vnd.ms-excel', 'application/xml', 'application/zip',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
```

    

.env:

```.env
AWS_DEFAULT_ACL=''
AWS_ACCESS_KEY_ID=''
AWS_SECRET_ACCESS_KEY=''
AWS_STORAGE_BUCKET_NAME=''
AWS_CACHE_CONTROL=86400
AWS_LOCATION=''
AWS_S3_FILE_OVERWRITE=False
```

urls.py


```python
from djangorestfilemanager.urls import router as file_manager_router

urlpatterns = [
    ...,
    path('', include(file_manager_router.urls))

]
```

#API REST ENDPOINTS:

Permission: Authentication is required. 

If user is superuser, can download all files.

If user is file owner, that user can download this file.

If file is shared (share==True) and user have perms, can download this file. 


Upload File

|  param      |  description                         |
| -------     |  -----------                         |
| url | /{{api}}/files/ | 
| methods | post |
| --- | --- |
| file        |  file object                         |
| type        |  string, max length 10 not required  |
| permission  |  string content_type.model +.+ permission.name  Example: user.can_create_user, default '' |
| share       |  bool, default true |
| data        |  jsonfield     |
| --- | --- |
| return_data | uuid |


Download File

| param | description |
| ----- | ----------- |
|  url  |      /{{api}}/files/{{uuid}}/       |
| --- | --- |
|  methods  |     get    |
| --- | --- |
|  return  |      download file.    |


#OVERRIDE ENDPOINTS
```python
DJANGO_REST_FILE_MANAGER_SERIALIZERS = {
    'FILE_SERIALIZER': '...',
    'FILE_VIEW_SERIALIZER': '...',
}
```
#OVERRIDE SETTINGS
```
REST_FILE_MANAGER = {
    'UPLOADS_DIR': os.environ.get('UPLOADS_DIR', default='media/'),
    'STATUS_CHOICES': (
        (PENDING, 'Pending'),
        ....
    )
    'DEFAULT_CHOICE':'' #STRING VALUE,
    'DEFAULT_SHAREABLE': Boolean, default True
}
```
# How to update to Pypi

When a new release is ready we have to make the package. Exec the following command (Remember to update setup.py with the current version of the package.)

```
python setup.py sdist
```

After that, we have to push our package to Pypi with `twine` (the first time we will have to install it)

```
twine upload dist/*
```

This command will upload every version existing on dist folder, we can specify one changing `dist/*` to the new dist file `dist/package_filename.gz`. 


