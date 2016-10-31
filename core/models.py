import os
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from core.utils import generate_random_hex


class FolderManager(TreeManager, models.Manager):
    def get_user_root(self, user):
        """Get user root folder (and create if necessary)."""
        users_folder, created = self.get_or_create(name='Users', parent=None, owner=None)
        user_root, created = self.get_or_create(name=str(user.id), parent=users_folder, owner=user)
        return user_root


class Folder(MPTTModel):
    name = models.CharField(_('name'), max_length=255)
    parent = TreeForeignKey('self', verbose_name=_('parent'), related_name='children', null=True, blank=True,
                            on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), related_name='owned_folders',
                              null=True, blank=False, on_delete=models.CASCADE)
    description = models.TextField(_('description'), null=True, blank=True)
    slug = models.SlugField(_('slug'), unique=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    objects = FolderManager()

    class MPTTMeta:
        order_insertion_by = ('name',)

    class Meta:
        unique_together = (('parent', 'name'),)
        ordering = ('name',)
        verbose_name = _('folder')
        verbose_name_plural = _('folders')

    def __str__(self):
        return self.name


class File(models.Model):
    def _upload_to(instance, filename):
        instance.original_filename = filename[:255]
        if instance.id:
            instance.save(update_fields=['original_filename'])
        basename, extension = os.path.splitext(filename)
        secure_filename = '%s_%s%s' % (basename, generate_random_hex(length=10), extension)
        return os.path.join('files/', now().date().strftime('%Y/%m/%d'), secure_filename)

    folder = TreeForeignKey(Folder, verbose_name=_('folder'), related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=_upload_to)
    name = models.CharField(_('name'), max_length=255, blank=True, default='')
    original_filename = models.CharField(_('original filename'), max_length=255, blank=True, default='')
    size = models.PositiveIntegerField(_('size'), blank=True, default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), related_name='owned_files',
                              on_delete=models.CASCADE)
    description = models.TextField(_('description'), null=True, blank=True)
    slug = models.SlugField(_('slug'), unique=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        ordering = ('name', 'original_filename')
        verbose_name = _('file')
        verbose_name_plural = _('files')

    def __str__(self):
        return self.name

    @property
    def extension(self):
        ext = os.path.splitext(self.file.name)[1].lower()
        # remove dot
        return ext[1:] if ext else ext
