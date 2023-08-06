from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.translation import gettext as _
from django.urls import reverse
# Create your models here.

class Human(models.Model):
    position = models.SmallIntegerField(unique=True, help_text="In which position is person listed", default=1)
    image = models.ImageField(upload_to='humansImages/', default='humansImages/default.webp', verbose_name=_("Person image"))
    name = models.TextField(null=True)
    role = models.TextField(null=True, help_text=_("Role inside of the organization"))
    shortDescription = RichTextUploadingField(null=True, blank=True)
    description = RichTextUploadingField(null=True, blank=True)
    isPublished = models.BooleanField(default=False, null=True, verbose_name="Published", help_text=_("After setting Yes, person wil be visible for all users, after setting No - for admins only "))
    customSlug = models.TextField(blank=False, null=False, verbose_name=_("Custom slug"), help_text=_("Slug that will lead to persons page, i.e. yourdomain.com/team/<slug>/"), unique=True)
    websiteUrl = models.URLField(null=True, blank=True)
    twitterUrl = models.URLField(null=True, blank=True)
    linkedInUrl = models.URLField(null=True, blank=True)
    class Meta:
        verbose_name_plural = "Humans"
    
    def get_absolute_url(self):
        return reverse('humansPersonPageView', kwargs={'personSlug': self.customSlug})