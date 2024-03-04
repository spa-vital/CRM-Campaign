from .models import Campaign
from django import forms
from dynfilters.models import DynamicFilterExpr
from django.db.models import Q
from django.utils.translation import gettext, gettext_lazy as _


class CreateCampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('name',)
    
    name = forms.CharField(widget=forms.TextInput(attrs={
    'class': ' w-1/2 py-4 px-2 mb-4 mt-2 rounded-xl bg-gray-100'
    }))
    def save(self, commit=True) -> Campaign:
        campaign = super().save(commit=False)
        if commit:
            campaign.save()

        return campaign


class CampaignRecipientsForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('mailing_list',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['tag'].queryset = Tag.objects.none()          
        print(DynamicFilterExpr.objects.filter(model="lead.Lead").order_by('name'))  
        self.fields['mailing_list'].queryset = DynamicFilterExpr.objects.filter(model="lead.Lead").order_by('name')
        # if 'tag' in self.data:
        #     try:
        #         mailing_list_id = int(self.data.get('mailing_list'))
        #         # self.fields['tag'].queryset = Tag.objects.filter(mailing_list_id=mailing_list_id).order_by('name')
        #     except (ValueError, TypeError):
        #         pass
        # elif self.instance.pk and self.instance.mailing_list:
        #     self.fields['tag'].queryset = self.instance.mailing_list.tags.order_by('name')

class EmailEditorForm(forms.Form):
    def __init__(self, email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = email
        blocks = email.get_blocks()
        for block_key, block_content in blocks.items():
            self.fields[block_key] = forms.CharField(
                label=_('Block %s' % block_key),
                required=False,
                initial=block_content,
                widget=forms.Textarea()
            )

    def save(self, commit=True):
        self.email.set_blocks(self.cleaned_data)
        if commit:
            self.email.save()
        return self.email