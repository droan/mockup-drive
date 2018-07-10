import os
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
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
    parent = TreeForeignKey('self', verbose_name=_('parent'), related_name='children', null=True, blank=False,
                            on_delete=models.CASCADE)
    owner = models.ForeignKey(get_user_model(), verbose_name=_('owner'), related_name='owned_folders',
                              null=True, blank=False, on_delete=models.CASCADE)
    description = models.TextField(_('description'), null=True, blank=True)
    slug = models.SlugField(_('slug'), unique=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    permissions = GenericRelation('Permission')

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

    @property
    def is_user_root(self):
        return str(self.owner.id) == self.name and self.level == 1

    def get_absolute_url(self):
        return reverse('core:folder-detail', args=[str(self.slug)])

    def get_user_ancestors(self):
        """Like mptt get_ancestors but without Users root folder."""
        return self.get_ancestors()[1:]

    def can_share(self, user):
        if self.owner == user:
            return True

    def has_permission(self, user, permission_category):
        if self.owner == user or user.is_superuser:
            return True
        elif self.permissions.filter(category=permission_category, everybody=True):
            return True
        elif user.is_authenticated and self.permissions.filter(category=permission_category, user=user):
            return True
        elif self.parent:
            return self.parent.has_permission(user, permission_category)
        else:
            return False


class File(models.Model):
    def _upload_to(instance, filename):
        instance.original_filename = filename[:255]
        if instance.id:
            instance.save(update_fields=['original_filename'])
        basename, extension = os.path.splitext(filename)
        secure_filename = '%s_%s%s' % (basename, generate_random_hex(length=10), extension)
        return os.path.join('files/', now().date().strftime('%Y/%m/%d'), secure_filename)

    folder = TreeForeignKey(Folder, verbose_name=_('folder'), related_name='files')
    file = models.FileField(upload_to=_upload_to)
    name = models.CharField(_('name'), max_length=255, blank=True, default='')
    original_filename = models.CharField(_('original filename'), max_length=255, blank=True, default='')
    size = models.PositiveIntegerField(_('size'), blank=True, default=0)
    owner = models.ForeignKey(get_user_model(), verbose_name=_('owner'), related_name='owned_files')
    description = models.TextField(_('description'), null=True, blank=True)
    slug = models.SlugField(_('slug'), unique=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    permissions = GenericRelation('Permission')

    class Meta:
        ordering = ('name', 'original_filename')
        verbose_name = _('file')
        verbose_name_plural = _('files')

    def __str__(self):
        return self.name

    @property
    def extension(self):
        """File extension in lower case without the dot."""
        ext = os.path.splitext(self.file.name)[1].lower()
        return ext[1:] if ext else ext

    @property
    def is_image(self):
        return self.extension in ['jpg', 'jpeg', 'png', 'gif']

    @property
    def is_document(self):
        return self.extension in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']

    def get_absolute_url(self):
        return reverse('core:file-detail', args=[str(self.slug)])

    def get_user_ancestors(self):
        """Like mptt get_ancestors but without Users root folder."""
        return self.folder.get_ancestors(include_self=True)[1:]

    def can_share(self, user):
        if self.owner == user:
            return True

    def has_permission(self, user, permission_category):
        if self.owner == user or user.is_superuser:
            return True
        elif self.permissions.filter(category=permission_category, everybody=True):
            return True
        elif user.is_authenticated and self.permissions.filter(category=permission_category, user=user):
            return True
        else:
            return self.folder.has_permission(user, permission_category)


class Permission(models.Model):
    CATEGORIES = Choices(
        ('r', 'view', _('View')),
        ('w', 'edit', _('Edit')),
    )

    def limit_choices_ct():
        ids = [ct.id for ct in ContentType.objects.get_for_models(Folder, File).values()]
        return {'id__in': ids}

    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name='+',
                                     limit_choices_to=limit_choices_ct)
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = GenericForeignKey('content_type', 'object_id')
    category = models.CharField(_('category'), choices=CATEGORIES, max_length=10, default=CATEGORIES.view)
    user = models.ForeignKey(get_user_model(), verbose_name=_('user'), related_name='permissions',
                             null=True, blank=True, on_delete=models.CASCADE)
    everybody = models.BooleanField(_('everybody'), default=False)

    class Meta:
        ordering = ('user', 'content_type')
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __str__(self):
        return '%s can %s' % (self.user or 'Everybody', self.get_category_display())

    def clean(self, *args, **kwargs):
        if self.content_type and self.object_id and self.content_object is None:
            raise ValidationError(_('Invalid object id.'))
        if not self.user and not self.everybody:
            raise ValidationError(_('User or "everybody" has to be selected.'))
        if self.user and self.everybody:
            raise ValidationError(_('User cannot be selected together with "everybody".'))
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_owner(self, user):
        if self.content_object.owner == user:
            return True
