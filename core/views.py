import logging
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView, DeleteView
from core.models import Folder, File, Permission
from core.forms import FolderForm, FileForm, PermissionForm

logger = logging.getLogger(__name__)


class PermissionMixin(SingleObjectMixin):
    permissions = (Permission.CATEGORIES.view,)

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            # self.object is required for SingleObjectMixin
            self.object = super().get_object(queryset=queryset)
        return self.object

    def extra_permission(self, obj):
        return True

    def _has_permission(self, user, obj):
        _permissions = [obj.has_permission(user, p) for p in self.permissions] + [self.extra_permission(obj)]
        return all(_permissions)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        msg = '%s %s for %s' % (request.user, self.permissions, obj)
        if not self._has_permission(request.user, obj):
            logger.debug('Deny ' + msg)
            raise PermissionDenied
        logger.debug('Allow ' + msg)
        return super().dispatch(request, *args, **kwargs)


class DenyRootFolderMixin:
    def dispatch(self, request, *args, **kwargs):
        home_url = reverse_lazy('core:home')
        if self.get_object().is_user_root and request.path != home_url:
            return redirect(home_url)
        return super().dispatch(request, *args, **kwargs)


class FolderDetailView(DenyRootFolderMixin, PermissionMixin, DetailView):
    model = Folder
    template_name = 'core/folder_detail.html'


class HomeView(LoginRequiredMixin, FolderDetailView):
    template_name = 'core/home.html'

    def get_object(self, queryset=None):
        return Folder.objects.get_user_root(self.request.user)


class FolderAddView(PermissionMixin, LoginRequiredMixin, FormView):
    model = Folder
    form_class = FolderForm
    permissions = (Permission.CATEGORIES.edit,)
    template_name = 'core/folder_add.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'initial': {'parent': self.get_object()},
        })
        return kwargs

    def form_valid(self, form):
        folder = form.save(commit=False)
        folder.owner = self.request.user
        folder.save()
        return redirect(folder.get_absolute_url())


class FolderEditView(DenyRootFolderMixin, PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Folder
    form_class = FolderForm
    permissions = (Permission.CATEGORIES.edit,)
    template_name = 'core/folder_edit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs


class FolderDeleteView(DenyRootFolderMixin, PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Folder
    permissions = (Permission.CATEGORIES.edit,)
    template_name = 'core/folder_delete.html'

    def get_success_url(self):
        try:
            return self.object.parent.get_absolute_url()
        except Exception:
            return reverse('core:home')


class FolderShareView(PermissionMixin, LoginRequiredMixin, FormView):
    model = Permission
    form_class = PermissionForm
    queryset = Folder.objects.all()
    context_object_name = 'folder'
    template_name = 'core/folder_share.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'initial': {
                'content_type': ContentType.objects.get_for_model(Folder),
                'object_id': self.get_object().id,
            },
        })
        return kwargs

    def extra_permission(self, obj):
        return obj.can_share(self.request.user)

    def form_valid(self, form):
        file = self.get_object()
        permission = form.save(commit=False)
        permission.content_type = ContentType.objects.get_for_model(Folder)
        permission.object_id = file.id
        permission.save()
        return redirect(file.get_absolute_url())


class FileDetailView(PermissionMixin, DetailView):
    model = File
    template_name = 'core/file_detail.html'


class FileAddView(PermissionMixin, LoginRequiredMixin, FormView):
    model = File
    form_class = FileForm
    queryset = Folder.objects.all()
    context_object_name = 'folder'
    permissions = (Permission.CATEGORIES.edit,)
    template_name = 'core/file_add.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'initial': {'folder': self.get_object()},
        })
        return kwargs

    def form_valid(self, form):
        file = form.save(commit=False)
        file.owner = self.request.user
        file.save()
        return redirect(file.get_absolute_url())


class FileEditView(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = File
    form_class = FileForm
    permissions = (Permission.CATEGORIES.edit,)
    template_name = 'core/file_edit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs


class FileDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = File
    permissions = (Permission.CATEGORIES.edit,)
    template_name = 'core/file_delete.html'

    def get_success_url(self):
        try:
            folder = self.object.folder
            return folder.get_absolute_url()
        except Exception:
            return reverse('core:home')


class FileShareView(PermissionMixin, LoginRequiredMixin, FormView):
    model = Permission
    form_class = PermissionForm
    queryset = File.objects.all()
    context_object_name = 'file'
    template_name = 'core/file_share.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'initial': {
                'content_type': ContentType.objects.get_for_model(File),
                'object_id': self.get_object().id,
            },
        })
        return kwargs

    def extra_permission(self, obj):
        return obj.can_share(self.request.user)

    def form_valid(self, form):
        file = self.get_object()
        permission = form.save(commit=False)
        permission.content_type = ContentType.objects.get_for_model(File)
        permission.object_id = file.id
        permission.save()
        return redirect(file.get_absolute_url())


class ShareDeleteView(PermissionMixin, LoginRequiredMixin, View):
    model = Permission
    permissions = []

    def extra_permission(self, obj):
        return obj.is_owner(self.request.user)

    def get(self, request, *args, **kwargs):
        success_url = 'core:home'
        try:
            permission = self.get_object()
            success_url = permission.content_object.get_absolute_url()
            permission.delete()
        except Exception as e:
            logger.exception(e)
        return redirect(success_url)
