from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from core.models import Folder, File

admin.site.site_title = _('Drive admin')
admin.site.site_header = _('Drive admin')


@admin.register(Folder)
class FolderAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('name', 'owner', 'slug', 'created')
    search_fields = ('name', 'owner__username', 'slug')
    list_filter = ('created', 'modified')
    date_hierarchy = 'created'
    readonly_fields = ('slug',)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    def size_human(self, obj):
        return filesizeformat(obj.size)
    size_human.short_description = 'Size'
    size_human.admin_order_field = 'size'

    list_display = ('name', 'original_filename', 'size_human', 'owner', 'slug', 'created')
    search_fields = ('name', 'original_filename', 'owner__username', 'slug')
    list_filter = ('created', 'modified')
    date_hierarchy = 'created'
    exclude = ('size',)
    readonly_fields = ('original_filename', 'size_human', 'slug')
