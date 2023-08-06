from django.urls import path, include

urlpatterns = [
    path('', include('kfsd.apps.frontend.urls')),
    path('apis/', include('kfsd.apps.endpoints.urls')),
]
