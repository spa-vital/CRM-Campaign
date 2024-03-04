from tealcrm.celeryconf import app
import re
import html2text
from django.apps import apps
from dynfilters.models import DynamicFilterExpr

from dynfilters.model_helpers import (
    get_model_admin,
    get_qualified_model_names,
    get_dynfilters_fields,
    get_dynfilters_select_related,
    get_dynfilters_prefetch_related,
)
from dynfilters.utils import flatten
from lead.models import Lead
from django.core.mail import send_mail


# from .api import send_campaign
# from django.core.mail import mail_managers

class CampaignStatus:
    SENT = 1
    SCHEDULED = 2
    DRAFT = 3
    QUEUED = 4
    DELIVERING = 5
    PAUSED = 6

def filter_user_to_send_email(id):
    queryset = Lead.objects.all()
    try:
        obj = DynamicFilterExpr.objects.get(pk=id)
    except DynamicFilterExpr.DoesNotExist:
        return queryset # filter no longer exists, ignore

    model_admin = get_model_admin(obj)
    elementary_fields = flatten([
        f.split('__') 
        for f, display in get_dynfilters_fields(model_admin)
        if f != '-'
    ])

    queryset = queryset.select_related(*[
        f 
        for f in get_dynfilters_select_related(model_admin)
        if f in elementary_fields
    ])

    queryset = queryset.prefetch_related(*[
        f 
        for f in get_dynfilters_prefetch_related(model_admin)
        if f in elementary_fields
    ])
    try:
        return queryset.filter(obj.as_q())
    except:
        return queryset

@app.task()
def send_campaign_task(campaign_id):
    Campaign = apps.get_model('campaigns', 'Campaign')
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        if campaign.status == CampaignStatus.QUEUED:
            campaign.status = CampaignStatus.DELIVERING
            campaign.save(update_fields=['status'])
            email = campaign.email
            context = {
            }
            rich_text_message = email.render(context)
            plain_text_message = html2text.html2text(rich_text_message, bodywidth=2000)
            plain_text_message = re.sub(r'(!\[\]\(https?://.*/track/open/.*/\)\n\n)', '', plain_text_message, 1)
            print(plain_text_message)
            #filter and send email:
            leads = filter_user_to_send_email(campaign.mailing_list.id)
            list_emails_send = [l.email for l in leads]
            print(list_emails_send)
            send_mail(email.from_email, plain_text_message,
                "Bảo Lâm <baolam.main@gmail.com>", list_emails_send)
            campaign.status = CampaignStatus.SENT
            campaign.save(update_fields=['status'])
        else:
            print('Campaign "%s" was placed in a queue with status "%s".' % (campaign_id,
                                                                                      campaign.get_status_display()))
    except Campaign.DoesNotExist:
        print('Campaign "%s" was placed in a queue but it does not exist.' % campaign_id)