from django import forms
from django.utils.translation import ugettext_lazy as _
from core.models import Folder, File, Permission


class FolderForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['parent'].choices = self._get_folder_choices(user, self.instance)

    def _get_folder_choices(self, user, instance):
        root = Folder.objects.get_user_root(user)
        descendants = root.get_descendants()
        if instance:
            descendants = descendants.exclude(id=instance.id)
        folders = [(f.id, '%s %s' % ('---'*(f.level - root.level), f.name)) for f in descendants]
        return [(root.id, _('Home'))] + folders

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent and parent == self.instance:
            raise forms.ValidationError(_('Invalid parent.'))
        if parent and not parent.has_permission(self.user, Permission.CATEGORIES.edit):
            raise forms.ValidationError(_('Invalid parent.'))
        return parent

    class Meta:
        model = Folder
        fields = ('parent', 'name', 'description')


class FileForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['folder'].choices = self._get_folder_choices(user, self.instance)

    def _get_folder_choices(self, user, instance):
        root = Folder.objects.get_user_root(user)
        descendants = root.get_descendants()
        folders = [(f.id, '%s %s' % ('---'*(f.level - root.level), f.name)) for f in descendants]
        return [(root.id, _('Home'))] + folders

    def clean_folder(self):
        folder = self.cleaned_data.get('folder')
        if folder and not folder.has_permission(self.user, Permission.CATEGORIES.edit):
            raise forms.ValidationError(_('Invalid folder.'))
        return folder

    class Meta:
        model = File
        fields = ('folder', 'file', 'name', 'description')


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ('category', 'user', 'everybody', 'content_type', 'object_id')
        widgets = {
            'content_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
        }
