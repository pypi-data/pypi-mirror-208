import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class GlobalPermissionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type__model='global_permission')

class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True
        verbose_name = "global_permission"

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label=self._meta.app_label,
        )
        self.content_type = ct
        super().save(*args)
        
class CloudspotUser(AbstractUser):
    id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    license_token = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey('CloudspotCompany', on_delete=models.SET_NULL, null=True, blank=True)
    pin = models.CharField(max_length=6, null=True, blank=True)

class CloudspotCompany(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    
    users = models.ManyToManyField('CloudspotUser', related_name="available_companies")