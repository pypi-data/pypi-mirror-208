from django.urls import path

from .views import (
    LiveDocumentCreateView,
    LiveDocumentDeleteView,
    LiveDocumentEditView,
    LiveDocumentListView,
    LiveDocumentShowAPIView,
    LiveDocumentShowView,
    PosterCurrentView,
    PosterDeleteView,
    PosterEditView,
    PosterGroupCreateView,
    PosterGroupDeleteView,
    PosterGroupEditView,
    PosterGroupListView,
    PosterListView,
    PosterUploadView,
)

urlpatterns = [
    path("", PosterListView.as_view(), name="poster_index"),
    path("upload/", PosterUploadView.as_view(), name="poster_upload"),
    path("<int:pk>/edit/", PosterEditView.as_view(), name="poster_edit"),
    path("<int:pk>/delete/", PosterDeleteView.as_view(), name="poster_delete"),
    path("<str:slug>.pdf", PosterCurrentView.as_view(), name="poster_show_current"),
    path("groups/", PosterGroupListView.as_view(), name="poster_group_list"),
    path("groups/create/", PosterGroupCreateView.as_view(), name="create_poster_group"),
    path("groups/<int:pk>/edit/", PosterGroupEditView.as_view(), name="edit_poster_group"),
    path("groups/<int:pk>/delete/", PosterGroupDeleteView.as_view(), name="delete_poster_group"),
    path("live/", LiveDocumentListView.as_view(), name="live_documents"),
    path(
        "live/<str:app>/<str:model>/create/",
        LiveDocumentCreateView.as_view(),
        name="create_live_document",
    ),
    path(
        "live/<int:pk>/edit/",
        LiveDocumentEditView.as_view(),
        name="edit_live_document",
    ),
    path(
        "live_documents/<int:pk>/delete/",
        LiveDocumentDeleteView.as_view(),
        name="delete_live_document",
    ),
    path(
        "live_documents/<str:slug>.pdf",
        LiveDocumentShowView.as_view(),
        name="show_live_document",
    ),
    path(
        "api/live_documents/<str:slug>.pdf",
        LiveDocumentShowAPIView.as_view(),
        name="api_show_live_document",
    ),
]
