from django.shortcuts import render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext, gettext_lazy as _

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import ContextMixin
from django.http import HttpResponse, JsonResponse
from .api import get_test_email_context
from .models import Campaign, CampaignStatus, CampaignTypes, Email
from .forms import CampaignRecipientsForm, CreateCampaignForm, EmailEditorForm


class CampaignMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        kwargs['menu'] = 'campaigns'
        return super().get_context_data(**kwargs)


class AbstractCampaignEmailUpdateView(CampaignMixin, UpdateView):
    model = Email
    template_name = 'campaigns/campaign_form.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.title
        kwargs['campaign'] = self.campaign
        return super().get_context_data(**kwargs)

    def get_object(self, queryset=None):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        return self.campaign.email

    def get_success_url(self):
        return reverse('campaign_edit', kwargs=self.kwargs)

# Create your views here.
@method_decorator(login_required, name='dispatch')
class CampaignListView(CampaignMixin, ListView):
    model = Campaign
    context_object_name = 'campaigns'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        kwargs['campaign_types'] = CampaignTypes
        kwargs['campaign_status'] = CampaignStatus
        kwargs['total_count'] = Campaign.objects.count()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.extra_context = {}

        queryset = super().get_queryset().select_related('mailing_list')

        try:
            status_filter = int(self.request.GET.get('status'))
            if status_filter in CampaignStatus.FILTERS:
                self.extra_context['status'] = status_filter
                queryset = queryset.filter(status=status_filter)
        except (ValueError, TypeError):
            pass

        if self.request.GET.get('q', ''):
            query = self.request.GET.get('q')
            queryset = queryset.filter(name__icontains=query)
            self.extra_context['is_filtered'] = True
            self.extra_context['query'] = query

        queryset = queryset.order_by('-update_date')

        return queryset


@method_decorator(login_required, name='dispatch')
class CampaignCreateView(CampaignMixin, CreateView):
    model = Campaign
    form_class = CreateCampaignForm

    def get_initial(self):
        initial = super().get_initial()
        mailing_list_id = self.request.GET.get('mailing_list', '')
        try:
            initial['mailing_list'] = int(mailing_list_id)
        except (TypeError, ValueError):
            pass
        return initial

@method_decorator(login_required, name='dispatch')
class CampaignEditView(CampaignMixin, DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaigns/campaign_edit.html'

    def get_queryset(self):
        return super().get_queryset() \
            .select_related('mailing_list') \
            .filter(status=CampaignStatus.DRAFT)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

@method_decorator(login_required, name='dispatch')
class CampaignEditRecipientsView(CampaignMixin, UpdateView):
    model = Campaign
    form_class = CampaignRecipientsForm
    context_object_name = 'campaign'
    template_name = 'campaigns/campaign_edit_recipients.html'



@method_decorator(login_required, name='dispatch')
class CampaignEditFromView(AbstractCampaignEmailUpdateView):
    title = _('From')
    fields = ('from_name', 'from_email',)

    def get_initial(self):
        if self.campaign.mailing_list is not None:
            pass
            # if self.campaign.email.from_email == '':
            #     self.initial['from_name'] = self.campaign.mailing_list.campaign_default_from_name
            #     self.initial['from_email'] = self.campaign.mailing_list.campaign_default_from_email
        return super().get_initial()

class CustomForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-1/2 py-4 px-2 mb-4 mt-2 rounded-xl bg-gray-100'}))
    preview = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-1/2 py-4 px-2 mb-4 mt-2 rounded-xl bg-gray-100'}))


@method_decorator(login_required, name='dispatch')
class CampaignEditSubjectView(AbstractCampaignEmailUpdateView):
    title = _('Subject')
    fields = ('subject', 'preview',)
    form_class = CustomForm()
    def get_initial(self):
        if self.campaign.mailing_list is not None:
            if self.campaign.email.subject == '':
                self.initial['subject'] = self.campaign.mailing_list.campaign_default_email_subject
        return super().get_initial()


@method_decorator(login_required, name='dispatch')
class CampaignEditTemplateView(AbstractCampaignEmailUpdateView):
    title = _('Template')
    fields = ('template',)

    def form_valid(self, form):
        email = form.save(commit=False)
        email.set_template_content()
        email.set_blocks()
        email.save()
        return redirect('campaign_edit_content', pk=self.kwargs.get('pk'))

@login_required
def load_list_tags(request):
    list_id = request.GET.get('id')
    pass

    # try:
    #     mailing_list = MailingList.objects.get(pk=list_id)
    #     tags = mailing_list.tags.order_by('name')
    # except MailingList.DoesNotExist:
    #     tags = list()

    # context = {
    #     'tags': tags
    # }
    # options = render_to_string('campaigns/_campaign_list_tags_options.html', context, request)
    # return JsonResponse({'options': options})

@method_decorator(login_required, name='dispatch')
class CampaignEditSubjectView(AbstractCampaignEmailUpdateView):
    title = _('Subject')
    fields = ('subject', 'preview',)

    def get_initial(self):
        return super().get_initial()

@login_required
def campaign_edit_content(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if not campaign.email.template_content:
        return redirect('campaign_edit_template', pk=pk)
    if request.method == 'POST':
        form = EmailEditorForm(campaign.email, data=request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get('action', 'save_changes') == 'save_changes':
                return redirect('campaign_edit_content', pk=pk)
            return redirect('campaign_edit', pk=pk)
    else:
        form = EmailEditorForm(campaign.email)
    return render(request, 'campaigns/email_form.html', {
        'campaign': campaign,
        'form': form
    })


@login_required
def campaign_preview_email(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    email = campaign.email
    if request.method == 'POST':
        form = EmailEditorForm(email, data=request.POST)
        if form.is_valid():
            email = form.save(commit=False)
    context = dict()
    test_context_dict = get_test_email_context(**context)
    html = email.render(test_context_dict)
    if 'application/json' in request.META.get('HTTP_ACCEPT'):
        return JsonResponse({'html': html})
    else:
        return HttpResponse(html)

@method_decorator(login_required, name='dispatch')
class SendCampaignCompleteView(CampaignMixin, DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaigns/send_campaign_done.html'

@login_required
def send_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)

    if campaign.status == CampaignStatus.SENT or not campaign.can_send:
        return redirect(campaign.get_absolute_url())

    if request.method == 'POST':
        campaign.send()
        return redirect('send_campaign_complete', pk=pk)

    return render(request, 'campaigns/send_campaign.html', {
        'menu': 'campaign',
        'campaign': campaign
    })


@method_decorator(login_required, name='dispatch')
class CampaignDeleteView(CampaignMixin, DeleteView):
    model = Campaign
    context_object_name = 'campaign'
    success_url = reverse_lazy('campaigns')

@method_decorator(login_required, name='dispatch')
class CampaignDetailView(CampaignMixin, DetailView):
    model = Campaign
    context_object_name = 'campaign'
    extra_context = {'submenu': 'details'}

@method_decorator(login_required, name='dispatch')
class CampaignReportsView(CampaignMixin, DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaigns/campaign_reports.html'
    extra_context = {'submenu': 'reports'}

    

