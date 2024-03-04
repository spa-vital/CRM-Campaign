from collections import OrderedDict
from datetime import timezone
import json
import re
from typing import Optional
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import uuid
from lead.models import Lead
from django.utils import timezone
from django.urls import reverse
from django.template import Context, Template
from django.db.models import Count, QuerySet
from django.utils.html import mark_safe
from django.contrib.sites.shortcuts import get_current_site
from bs4 import BeautifulSoup
from django.utils.crypto import get_random_string
from django.template.base import VariableNode
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode
from dynfilters.models import DynamicFilterExpr
from templates.models import EmailTemplate
from .tasks import send_campaign_task

BLOCK_RE = re.compile(r'{%\s*block\s*(\w+)\s*%}')
NAMED_BLOCK_RE = r'{%%\s*block\s*%s\s*%%}'  # Accepts string formatting
ENDBLOCK_RE = re.compile(r'{%\s*endblock\s*(?:\w+\s*)?%}')

START_BLOCK_DIV = '''<div style="padding:10px;border:1px solid #bbb;background-color:#f9f9f9;margin-bottom:10px;">
<h4 style="text-align:center;color:#bbb;margin:0 0 5px;">%s</h4>'''
END_BLOCK_DIV = '</div>'

def get_block_source(template_source, block_name):
    """
    Given a template's source code, and the name of a defined block tag,
    returns the source inside the block tag.
    """
    # Find the open block for the given name
    match = re.search(NAMED_BLOCK_RE % (block_name,), template_source)
    if match is None:
        raise ValueError('Template block %s not found' % block_name)
    end = inner_start = start = match.end()
    end_width = 0
    while True:
        # Set ``end`` current end to just out side the previous end block
        end += end_width
        # Find the next end block
        match = re.search(ENDBLOCK_RE, template_source[end:])
        # Set ``end`` to just inside the next end block
        end += match.start()
        # Get the width of the end block, in case of another iteration
        end_width = match.end() - match.start()
        # Search for any open blocks between any previously found open blocks,
        # and the current ``end``
        nested = re.search(BLOCK_RE, template_source[inner_start:end])
        if nested is None:
            # Nothing found, so we have the correct end block
            break
        else:
            # Nested open block found, so set our nested search cursor to just
            # past the inner open block that was found, and continue iteration
            inner_start += nested.end()
    # Return the value between our ``start`` and final ``end`` locations
    return template_source[start:end]

def get_template_blocks(template):
    nodes = template.nodelist.get_nodes_by_type(BlockNode)
    blocks = OrderedDict()
    for node in nodes:
        blocks[node.name] = get_block_source(template.source, node.name)
    return blocks

def wrap_blocks(template_source):
    block_names = re.findall(BLOCK_RE, template_source)
    for block_name in block_names:
        template_source = re.sub(NAMED_BLOCK_RE % block_name, START_BLOCK_DIV % block_name, template_source)
    template_source = re.sub(ENDBLOCK_RE, END_BLOCK_DIV, template_source)
    return template_source

class ActivityTypes:
    SUBSCRIBED = 1
    UNSUBSCRIBED = 2
    SENT = 3
    OPENED = 4
    CLICKED = 5
    IMPORTED = 6
    CLEANED = 7

    LABELS = {
        SUBSCRIBED: _('Subscribed'),
        UNSUBSCRIBED: _('Unsubscribed'),
        SENT: _('Was sent'),
        OPENED: _('Opened'),
        CLICKED: _('Clicked'),
        IMPORTED: _('Imported'),
        CLEANED: _('Cleaned'),
    }

    CHOICES = tuple(LABELS.items())



class CampaignTypes:
    REGULAR = 1
    AUTOMATED = 2
    AB_TEST = 3

    LABELS = {
        REGULAR: _('Regular'),
        AUTOMATED: _('Automated'),
        AB_TEST: _('A/B Test'),
    }

    CHOICES = tuple(LABELS.items())


class CampaignStatus:
    SENT = 1
    SCHEDULED = 2
    DRAFT = 3
    QUEUED = 4
    DELIVERING = 5
    PAUSED = 6

    FILTERS = {SENT, SCHEDULED, DRAFT}

    ICONS = {
        SENT: 'fas fa-check',
        SCHEDULED: 'far fa-calendar',
        DRAFT: 'fas fa-pencil-alt'
    }

    LABELS = {
        SENT: _('Sent'),
        SCHEDULED: _('Scheduled'),
        DRAFT: _('Draft'),
        QUEUED: _('Queued'),
        DELIVERING: _('Delivering'),
        PAUSED: _('Paused'),
    }

    CHOICES = tuple(LABELS.items())

# Create your models here.
class Campaign(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(_('name'), max_length=100)
    campaign_type = models.PositiveSmallIntegerField(
        _('type'),
        choices=CampaignTypes.CHOICES,
        default=CampaignTypes.REGULAR
    )
    mailing_list = models.ForeignKey(
        DynamicFilterExpr,
        on_delete=models.CASCADE,
        verbose_name=_('mailing list'),
        related_name='campaigns',
        null=True,
        blank=True
    )
    status = models.PositiveSmallIntegerField(
        _('status'),
        choices=CampaignStatus.CHOICES,
        default=CampaignStatus.DRAFT,
        db_index=True
    )
    send_date = models.DateTimeField(_('send date'), null=True, blank=True, db_index=True)
    create_date = models.DateTimeField(_('create date'), auto_now_add=True)
    update_date = models.DateTimeField(_('update date'), default=timezone.now)
    recipients_count = models.PositiveIntegerField(default=0)
    track_opens = models.BooleanField(_('track opens'), default=True)
    track_clicks = models.BooleanField(_('track clicks'), default=True)
    unique_opens_count = models.PositiveIntegerField(_('unique opens'), default=0, editable=False)
    total_opens_count = models.PositiveIntegerField(_('total opens'), default=0, editable=False)
    unique_clicks_count = models.PositiveIntegerField(_('unique clicks'), default=0, editable=False)
    total_clicks_count = models.PositiveIntegerField(_('total clicks'), default=0, editable=False)
    open_rate = models.FloatField(_('opens'), default=0.0, editable=False)
    click_rate = models.FloatField(_('clicks'), default=0.0, editable=False)

    __cached_email = None

    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')
    
    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        if self.can_edit:
            return reverse('campaign_edit', kwargs={'pk': self.pk})
        elif self.is_scheduled:
            return reverse('campaign_scheduled', kwargs={'pk': self.pk})
        return reverse('campaign_detail', kwargs={'pk': self.pk})

    @property
    def is_scheduled(self) -> bool:
        return self.status == CampaignStatus.SCHEDULED

    @property
    def can_edit(self) -> bool:
        return self.status == CampaignStatus.DRAFT

    @property
    def can_send(self) -> bool:
            return True

    @property
    def email(self) -> Optional['Email']:
        if not self.__cached_email and self.campaign_type == CampaignTypes.REGULAR:
            try:
                self.__cached_email, created = Email.objects.get_or_create(campaign=self)
            except Email.MultipleObjectsReturned:
                self.__cached_email = self.emails.order_by('id').first()
        return self.__cached_email

    def send(self):
        with transaction.atomic():
            self.send_date = timezone.now()
            self.status = CampaignStatus.QUEUED
            for email in self.emails.select_related('template').all():
                if email.template is not None:
                    email.template.last_used_date = timezone.now()
                    email.template.last_used_campaign_id = self.pk
                    email.template.save()
            self.save()
        send_campaign_task.delay(self.pk)




class Email(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name=_('campaign'), related_name='emails')
    template_content = models.TextField(_('email template content'), blank=True)
    from_email = models.EmailField(_('email address'))
    from_name = models.CharField(_('name'), max_length=100, blank=True)
    subject = models.CharField(_('subject'), max_length=150)
    preview = models.CharField(_('preview'), max_length=150, blank=True)
    content = models.TextField(_('content'), blank=True)
    content_html = models.TextField(_('content HTML'), blank=True)
    content_text = models.TextField(_('content plain text'), blank=True)
    unique_opens_count = models.PositiveIntegerField(_('unique opens'), default=0, editable=False)
    total_opens_count = models.PositiveIntegerField(_('total opens'), default=0, editable=False)
    unique_clicks_count = models.PositiveIntegerField(_('unique clicks'), default=0, editable=False)
    total_clicks_count = models.PositiveIntegerField(_('total clicks'), default=0, editable=False)
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        verbose_name=_('email template'),
        related_name='emails',
        null=True,
        blank=True
    )

    __blocks = None
    __base_template = None
    __child_template_string = None

    BASE_TEMPLATE_VAR = 'base_template'

    class Meta:
        verbose_name = _('email')
        verbose_name_plural = _('emails')

    def __str__(self):
        return self.subject

    @property
    def base_template(self) -> Template:
        if self.__base_template is None:
            self.__base_template = Template(self.template_content)
        return self.__base_template

    @property
    def child_template_string(self) -> str:
        if self.__child_template_string is None:
            self.__child_template_string = self.build_child_template_string()
        return self.__child_template_string

    def set_template_content(self):
        if self.template is None:
            self.template_content = EmailTemplate.objects.default_content()
        else:
            self.template_content = self.template.content

    def get_from(self) -> str:
        if self.from_name:
            return '%s <%s>' % (self.from_name, self.from_email)
        return self.from_email

    def get_base_template(self) -> Template:
        """
        Retuns a Django template using `template_content` field.
        Fallback to default basic template defined by EmailTemplate.
        """
        if self.template_content:
            template = Template(self.template_content)
        else:
            template_string = EmailTemplate.objects.default_content()
            template = Template(template_string)
        return template

    def set_blocks(self, blocks=None):
        if blocks is None:
            old_blocks = self.get_blocks()
            blocks = dict()
            template = self.get_base_template()
            template_blocks = get_template_blocks(template)
            for block_name, block_content in template_blocks.items():
                inherited_content = block_content
                if block_name in old_blocks.keys():
                    old_block_content = old_blocks.get(block_name, '').strip()
                    if old_block_content:
                        inherited_content = old_blocks[block_name]
                blocks[block_name] = inherited_content
        self.content = json.dumps(blocks)
        self.__blocks = blocks

    def load_blocks(self) -> dict:
        try:
            blocks = json.loads(self.content)
        except (TypeError, json.JSONDecodeError):
            blocks = {'content': ''}
        return blocks

    def get_blocks(self) -> dict:
        if self.__blocks is None:
            self.__blocks = self.load_blocks()
        return self.__blocks

    def checklist(self) -> dict:
        _checklist = {
            'recipients': False,
            'from': False,
            'subject': False,
            'content': False,
            'unsub': False
        }

        if self.campaign.mailing_list is not None and self.campaign.mailing_list.get_active_subscribers().exists():
            _checklist['recipients'] = True

        if self.from_email:
            _checklist['from'] = True

        if self.subject:
            _checklist['subject'] = True

        if self.content:
            _checklist['content'] = True

            # Generate a random string and pass it to the render function
            # as if it was the unsubscribe url. If we can find this token in the
            # rendered template, we can say the unsubscribe url will be rendered.
            # Not 100% guranteed, as the end user can still bypass it (e.g.
            # changing visibility with html).
            token = get_random_string(50)
            rendered_template = self.render({'unsub': token})
            _checklist['unsub'] = token in rendered_template

        return _checklist

    @property
    def can_send(self) -> bool:
        checklist = self.checklist()
        for value in checklist.values():
            if not value:
                return False
        else:
            return True

    def build_child_template_string(self) -> str:
        """
        Build a valid Django template string with `extends` block tag
        on top and representation of each content blocks, constructed
        from the JSON object.
        """
        virtual_template = ['{%% extends %s %%}' % self.BASE_TEMPLATE_VAR, ]
        blocks = self.get_blocks()
        for block_key, block_content in blocks.items():
            if block_content:
                virtual_template.append('{%% block %s %%}\n%s\n{%% endblock %%}' % (block_key, block_content))
        return '\n\n'.join(virtual_template)

    def _render(self, template_string, context_dict) -> str:
        template = Template(template_string)
        context = Context(context_dict)
        return template.render(context)

    def render(self, context_dict) -> str:
        context_dict.update({self.BASE_TEMPLATE_VAR: self.base_template})
        return self._render(self.child_template_string, context_dict)


    def enable_click_tracking(self):
        self.template_content, index = self._enable_click_tracking(self.template_content)
        blocks = self.get_blocks()
        for key, html in blocks.items():
            blocks[key], index = self._enable_click_tracking(html, index)
        self.set_blocks(blocks)

    def enable_open_tracking(self):
        current_site = get_current_site(request=None)
        protocol = 'http'
        domain = current_site.domain
        track_url = '%s://%s/track/open/%s/{{uuid}}/' % (protocol, domain, self.uuid)
        soup = BeautifulSoup(self.template_content, 'html.parser')
        img_tag = soup.new_tag('img', src=track_url, height='1', width='1')
        body = soup.find('body')
        if body is not None:
            body.append(img_tag)
            self.template_content = str(soup)
        else:
            self.template_content = '%s %s' % (self.template_content, img_tag)

    def update_clicks_count(self) -> tuple:
        qs = self.activities.filter(activity_type=ActivityTypes.CLICKED) \
            .values('subscriber_id') \
            .order_by('subscriber_id') \
            .aggregate(unique_count=Count('subscriber_id', distinct=True), total_count=Count('subscriber_id'))
        self.unique_clicks_count = qs['unique_count']
        self.total_clicks_count = qs['total_count']
        self.save(update_fields=['unique_clicks_count', 'total_clicks_count'])
        return (self.unique_clicks_count, self.total_clicks_count)

    def update_opens_count(self) -> tuple:
        qs = self.activities.filter(activity_type=ActivityTypes.OPENED) \
            .values('subscriber_id') \
            .order_by('subscriber_id') \
            .aggregate(unique_count=Count('subscriber_id', distinct=True), total_count=Count('subscriber_id'))
        self.unique_opens_count = qs['unique_count']
        self.total_opens_count = qs['total_count']
        self.save(update_fields=['unique_opens_count', 'total_opens_count'])
        return (self.unique_opens_count, self.total_opens_count)
