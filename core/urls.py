from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from core.views import (
    HomeView, FolderDetailView, FolderAddView, FolderEditView, FolderDeleteView, FolderShareView,
    FileDetailView, FileAddView, FileEditView, FileDeleteView, FileShareView, ShareDeleteView
 )

urlpatterns = [
    url(r'^my/$', login_required(HomeView.as_view()), name='home'),
    url(r'^folder/(?P<slug>[-\w]+)/$', FolderDetailView.as_view(), name='folder-detail'),
    url(r'^folder/(?P<slug>[-\w]+)/add/$', login_required(FolderAddView.as_view()), name='folder-add'),
    url(r'^folder/(?P<slug>[-\w]+)/edit/$', login_required(FolderEditView.as_view()), name='folder-edit'),
    url(r'^folder/(?P<slug>[-\w]+)/delete/$', login_required(FolderDeleteView.as_view()), name='folder-delete'),
    url(r'^folder/(?P<slug>[-\w]+)/share/$', login_required(FolderShareView.as_view()), name='folder-share'),

    url(r'^file/(?P<slug>[-\w]+)/$', FileDetailView.as_view(), name='file-detail'),
    url(r'^file/(?P<slug>[-\w]+)/add/$', login_required(FileAddView.as_view()), name='file-add'),
    url(r'^file/(?P<slug>[-\w]+)/edit/$', login_required(FileEditView.as_view()), name='file-edit'),
    url(r'^file/(?P<slug>[-\w]+)/delete/$', login_required(FileDeleteView.as_view()), name='file-delete'),
    url(r'^file/(?P<slug>[-\w]+)/share/$', login_required(FileShareView.as_view()), name='file-share'),

    url(r'^permission/(?P<pk>[-\w]+)/delete/$', login_required(ShareDeleteView.as_view()), name='permission-delete'),
]
