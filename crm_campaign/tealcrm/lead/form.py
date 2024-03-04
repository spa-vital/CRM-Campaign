from django import forms
from .models import Lead, Comment, LeadFile, Product, LeadSource


class AddLeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ('name', 'email', 'description','phone', 'priority', 'status', 'product_line', 'company','job','lead_source',)
    

    name = forms.CharField(widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))
    email = forms.CharField(widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))
    description = forms.CharField( required=False, widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))
    phone = forms.CharField( required=False, widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))

    priority = forms.ChoiceField(choices=Lead.CHOICES_PRIORITY, widget=forms.Select(attrs={'class': 'w-full py-4 px-6 rounded-xl bg-gray-100'}))
    status = forms.ChoiceField(choices=Lead.CHOICES_STATUS, widget=forms.Select(attrs={'class': 'w-full py-4 px-6 rounded-xl bg-gray-100'}))

    product_line = forms.ModelChoiceField(queryset=Product.objects.all(), 
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'w-full py-4 px-6 rounded-xl bg-gray-100'}))


    company = forms.CharField( required=False, widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))

    job = forms.CharField( required=False, widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))

    lead_source = forms.ModelChoiceField(queryset=LeadSource.objects.all(), 
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'w-full py-4 px-6 rounded-xl bg-gray-100'}))

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

    content = forms.CharField(widget=forms.TextInput(attrs={
    'placeholder': 'Your comment',
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))


class AddFileForm(forms.ModelForm):
    class Meta:
        model = LeadFile
        fields = ('file',)
    
