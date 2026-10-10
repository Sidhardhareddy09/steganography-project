"""stegano_project URL Configuration

The `urlpatterns` list routes URLs to views.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from stegano_app import views

app_name = "stegano_project"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("encryption/", views.encryption_view, name="encryption"),
    path("decryption/", views.decryption_view, name="decryption"),
]

# In development, serve media files through Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
