# Django
from django.urls import include, path

# DRF
from rest_framework.routers import DefaultRouter

# Views
from sharepoint import views

# ViewSets

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('sharepoint-authorization/', views.SharepointAuthorizationAPIView.as_view()),
    path('folder/', views.SharePointFolderView.as_view()),
    path('folder-info/', views.SharePointFileInfoView.as_view()),
    path('file/', views.SharePointFileView.as_view()),
    path('refresh/', views.SharepointAuthorizationRefreshAPIView.as_view()),
    path('updated-info/', views.FileUpdateSharepointAPIView.as_view()),
    path('copy-file/', views.CopyFilesSharepointView.as_view()),
    path('move-file/', views.MoveFilesSharepointView.as_view()),
    path('create-folder-structure/', views.FolderStructureSharepointView.as_view()),
    path('delete-slide/', views.DeleteSlidesSharepointAPIView.as_view()),
    # path('merge-file/', views.MergeFilesSharepointAPIView.as_view()),

]