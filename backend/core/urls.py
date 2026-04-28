from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel — useful for debugging during development
    path('admin/', admin.site.urls),

    # All API routes are handled by api/urls.py
    # Example: /api/analyze/, /api/health/
    path('api/', include('api.urls')),
]