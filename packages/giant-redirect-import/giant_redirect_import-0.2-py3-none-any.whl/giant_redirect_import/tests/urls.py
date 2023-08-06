from django.urls import path
from django.contrib import admin

""""
Url patterns for testing
"""

urlpatterns = [
    path("admin/", admin.site.urls),
]
