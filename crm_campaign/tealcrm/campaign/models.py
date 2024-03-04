
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.sites.models import Site
# from django.conf import settings
# from django.utils.module_loading import import_string
# from django.db import models

# class Newsletter(models.Model):
    
#     name = models.CharField(_("Name"), max_length=255)
#     description = models.TextField(_("Description"), blank=True, null=True)
#     from_email = models.EmailField(_("Sending Address"), blank=True, null=True)
#     from_name = models.CharField(_("Sender Name"), max_length=255, blank=True, null=True)
#     site = models.ForeignKey(Site, verbose_name=_("Site"), on_delete=models.SET_NULL, blank=True, null=True)
#     default = models.BooleanField(_("Default"), default=False)

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = _("newsletter")
#         verbose_name_plural = _("newsletters")
#         ordering = ('name',)


# class MailTemplate(models.Model):

#     name = models.CharField(_("Name"), max_length=255)
#     plain = models.TextField(_("Plaintext Body"))
#     html = models.TextField(_("HTML Body"), blank=True, null=True)
#     subject = models.CharField(_("Subject"), max_length=255)

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = _("mail template")
#         verbose_name_plural = _("mail templates")
#         ordering = ('name',)


# class SubscriberList(models.Model):

#     name = models.CharField(_("Name"), max_length=255)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=ContentType._meta.verbose_name, null=True, blank=True)
#     filter_condition = models.JSONField(help_text=_("Django ORM compatible lookup kwargs which are used to get the list of objects."), null=True, blank=True)
#     email_field_name = models.CharField(_("Email-Field name"), max_length=64, help_text=_("Name of the model field which stores the recipients email address"))
#     custom_list = models.CharField(max_length=255, choices=getattr(settings, 'CAMPAIGN_CUSTOM_SUBSCRIBER_LISTS', []), null=True, blank=True)

#     def __str__(self):
#         return self.name


#     class Meta:
#         verbose_name = _("subscriber list")
#         verbose_name_plural = _("subscriber lists")
#         ordering = ('name',)


# class Campaign(models.Model):
  
#     name = models.CharField(_("Name"), max_length=255)
#     newsletter = models.ForeignKey(Newsletter, verbose_name=_("Newsletter"), blank=True, null=True, on_delete=models.CASCADE)
#     template = models.ForeignKey(MailTemplate, verbose_name=_("Template"), on_delete=models.CASCADE)
#     modified_date = models.DateField(auto_now_add=True),
#     description = models.TextField(blank= True, null= True)


#     def __str__(self):
#         return self.name


#     class Meta:
#         verbose_name = _("campaign")
#         verbose_name_plural = _("campaigns")
#         ordering = ('name', 'sent')
#         permissions = (
#             ("send_campaign", _("Can send campaign")),
#         )


# class BlacklistEntry(models.Model):

#     email = models.EmailField()
#     added = models.DateTimeField(default=timezone.now, editable=False)
#     reason = models.TextField(_("reason"), blank=True, null=True)

#     def __str__(self):
#         return self.email

#     class Meta:
#         verbose_name = _("blacklist entry")
#         verbose_name_plural = _("blacklist entries")
#         ordering = ('-added',)
