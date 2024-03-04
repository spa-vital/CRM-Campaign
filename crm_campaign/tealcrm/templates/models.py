import re
from django.db import models
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

BLOCK_RE = re.compile(r'{%\s*block\s*(\w+)\s*%}')
NAMED_BLOCK_RE = r'{%%\s*block\s*%s\s*%%}'  # Accepts string formatting
ENDBLOCK_RE = re.compile(r'{%\s*endblock\s*(?:\w+\s*)?%}')

START_BLOCK_DIV = '''<div style="padding:10px;border:1px solid #bbb;background-color:#f9f9f9;margin-bottom:10px;">
<h4 style="text-align:center;color:#bbb;margin:0 0 5px;">%s</h4>'''
END_BLOCK_DIV = '</div>'


def wrap_blocks(template_source):
    block_names = re.findall(BLOCK_RE, template_source)
    for block_name in block_names:
        template_source = re.sub(NAMED_BLOCK_RE % block_name, START_BLOCK_DIV % block_name, template_source)
    template_source = re.sub(ENDBLOCK_RE, END_BLOCK_DIV, template_source)
    return template_source

# Create your models here.
class EmailTemplateManager(models.Manager):
    @classmethod
    def default_content(cls):
        default_content = get_template('templates/default_email_template_content.html')
        content = default_content.template.source
        return content


class EmailTemplate(models.Model):
    name = models.CharField(_('name'), max_length=100)
    content = models.TextField(blank=True)
    create_date = models.DateTimeField(_('create date'), auto_now_add=True)
    update_date = models.DateTimeField(_('update date'), default=timezone.now)
    last_used_date = models.DateTimeField(_('last used'), null=True, blank=True)
    last_used_campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('last used campaign'),
        related_name='+'
    )

    objects = EmailTemplateManager()

    class Meta:
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')
        db_table = 'colossus_email_templates'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and not self.content:
            self.content = self.__class__.objects.default_content()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('templates:emailtemplate_editor', kwargs={'pk': self.pk})

    def html_preview(self):
        html = wrap_blocks(self.content)
        return mark_safe(html)