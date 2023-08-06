from django.urls import path, re_path
from django.views.generic.base import RedirectView
from kfsd.apps.frontend.views.docs.api import APIDocsView

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='apis/doc/', permanent=False), name='api_doc'),
    path('apis/doc/', APIDocsView.as_view(), name="api_doc"),
]
