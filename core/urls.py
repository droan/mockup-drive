from django.conf.urls import url
from core.views import (
    HomeView, FolderDetailView, FolderAddView, FolderEditView, FolderDeleteView, FolderShareView,
    FileDetailView, FileAddView, FileEditView, FileDeleteView, FileShareView, ShareDeleteView
)

urlpatterns = [
    url(r'^my/$', HomeView.as_view(), name='home'),
    url(r'^folder/(?P<slug>[-\w]+)/$', FolderDetailView.as_view(), name='folder-detail'),
    url(r'^folder/(?P<slug>[-\w]+)/add/$', FolderAddView.as_view(), name='folder-add'),
    url(r'^folder/(?P<slug>[-\w]+)/edit/$', FolderEditView.as_view(), name='folder-edit'),
    url(r'^folder/(?P<slug>[-\w]+)/delete/$', FolderDeleteView.as_view(), name='folder-delete'),
    url(r'^folder/(?P<slug>[-\w]+)/share/$', FolderShareView.as_view(), name='folder-share'),

    url(r'^file/(?P<slug>[-\w]+)/$', FileDetailView.as_view(), name='file-detail'),
    url(r'^file/(?P<slug>[-\w]+)/add/$', FileAddView.as_view(), name='file-add'),
    url(r'^file/(?P<slug>[-\w]+)/edit/$', FileEditView.as_view(), name='file-edit'),
    url(r'^file/(?P<slug>[-\w]+)/delete/$', FileDeleteView.as_view(), name='file-delete'),
    url(r'^file/(?P<slug>[-\w]+)/share/$', FileShareView.as_view(), name='file-share'),

    url(r'^permission/(?P<pk>[-\w]+)/delete/$', ShareDeleteView.as_view(), name='permission-delete'),
]
