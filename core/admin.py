from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from core.models import Folder, File, Permission

admin.site.site_title = _('Drive admin')
admin.site.site_header = _('Drive admin')


@admin.register(Folder)
class FolderAdmin(MPTTModelAdmin):
    def slug_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.get_absolute_url(), obj.slug)
    slug_link.short_description = 'Slug'
    slug_link.admin_order_field = 'slug'
    slug_link.allow_tags = True

    mptt_level_indent = 10
    list_display = ('name', 'owner', 'slug_link', 'created')
    search_fields = ('name', 'owner__username', 'slug')
    list_filter = ('created', 'modified')
    date_hierarchy = 'created'
    readonly_fields = ('slug',)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    def slug_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.get_absolute_url(), obj.slug)
    slug_link.short_description = 'Slug'
    slug_link.admin_order_field = 'slug'
    slug_link.allow_tags = True

    def size_human(self, obj):
        return filesizeformat(obj.size)
    size_human.short_description = 'Size'
    size_human.admin_order_field = 'size'

    list_display = ('name', 'original_filename', 'size_human', 'owner', 'slug_link', 'created')
    search_fields = ('name', 'original_filename', 'owner__username', 'slug')
    list_filter = ('created', 'modified')
    date_hierarchy = 'created'
    ordering = ('-created', 'name')
    exclude = ('size',)
    readonly_fields = ('original_filename', 'size_human', 'slug')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    def content_object_name(self, obj):
        return str(obj.content_object)
    content_object_name.short_description = 'Content object'

    def content_object_link(self, obj):
        try:
            return '<a href="%s">%s</a>' % (obj.content_object.get_absolute_url(), obj.content_object)
        except:
            return ''
    content_object_link.short_description = 'Content link'
    content_object_link.allow_tags = True

    list_display = ('content_object_name', 'content_type', 'category', 'user', 'everybody')
    search_fields = ('user__username',)
    list_filter = ('content_type', 'category', 'everybody')
    readonly_fields = ('content_object_link',)
