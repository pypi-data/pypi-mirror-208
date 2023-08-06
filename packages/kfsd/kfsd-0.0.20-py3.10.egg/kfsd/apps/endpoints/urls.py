from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from rest_framework import routers
from kfsd.apps.endpoints.views.utils.utils import UtilsViewSet
from kfsd.apps.endpoints.views.utils.common import CommonViewSet

router = routers.DefaultRouter()
router.include_format_suffixes = False

router.register("utils", UtilsViewSet, basename="utils")
router.register("common", CommonViewSet, basename="common")

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema-api'),
]
