import logging
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from core.models import Folder, File
from core.utils import generate_random_hex

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Folder)
@receiver(pre_save, sender=File)
def folder_file_generate_slug(sender, instance, **kwargs):
    if not instance.slug:
        exists = True
        while exists:
            slug = generate_random_hex(length=20)
            exists = instance.__class__.objects.filter(slug=slug).exists()
        instance.slug = slug


@receiver(pre_save, sender=File)
def file_set_info(sender, instance, **kwargs):
    try:
        if not instance.name:
            instance.name = instance.original_filename
        if not instance.size:
            instance.size = instance.file.size
    except Exception as e:
        logger.exception(e)


@receiver(post_delete, sender=File)
def file_delete_file(sender, instance, **kwargs):
    try:
        # Delete the file if there are no other Files referencing it.
        if not File.objects.filter(file=instance.file.name).exists():
            instance.file.delete(save=False)
    except Exception as e:
        logger.exception(e)
