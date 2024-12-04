# Django
from django.urls import include, path

# DRF
from rest_framework.routers import DefaultRouter

# Views
from rag import views


router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('search-sharepoint/', views.IndexationAPIView.as_view()),
    path('upload-file/', views.FileUploadAPIView.as_view()),  
    path('create-rag-services/', views.CreateRAGServicesAPIView.as_view()),
]