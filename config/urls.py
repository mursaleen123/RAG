# Django
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

# DRF
from rest_framework.routers import DefaultRouter



router = DefaultRouter()

urlpatterns = [
    path(r'', include(router.urls)),

    # Admin
    path(settings.ADMIN_URL, admin.site.urls),

    # APIs
    path('rag-api/', include(('rag.urls', 'rag'), namespace='rag-api')),
    path('sharepoint-api/', include(('sharepoint.urls', 'sharepoint'), namespace='sharepoint-api')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.autodiscover()