from django.urls import include
from django.conf.urls import url
from rest_framework import routers

from djangorestfilemanager.views import FileModelViewSet

router = routers.SimpleRouter()
router.register(r'(?P<version>(v1))/files', FileModelViewSet)

urlpatterns = router.urls
