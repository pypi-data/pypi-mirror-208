"""
This urlconf exists because Django expects ROOT_URLCONF to exist. URLs
should be added within the test folders, and use TestCase.urls to set them.
This helps the tests remain isolated.
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path

urlpatterns = [
    path("authenticator/", include("authenticator.urls")),
    path("", admin.site.urls),
]
