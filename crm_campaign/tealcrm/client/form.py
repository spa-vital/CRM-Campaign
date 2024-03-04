from django import forms

from .models import Client, Comment, ClientFile
from product.models import Product

class AddClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'email', 'description','phone', 'product_line','company','job',)

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

    product_line = forms.ModelChoiceField(queryset=Product.objects.all(), 
                                          required=False,
                                          widget=forms.Select(attrs={'class': 'w-full py-4 px-6 rounded-xl bg-gray-100'}))


    company = forms.CharField( required=False, widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))

    job = forms.CharField( required=False, widget=forms.TextInput(attrs={
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))
    

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
    content = forms.CharField(label=False, widget=forms.TextInput(attrs={
    'placeholder': 'Your comment',
    'class': ' w-full py-4 px-6 rounded-xl bg-gray-100'
    }))

class AddFileForm(forms.ModelForm):
    class Meta: 
        model = ClientFile
        fields = ('file',)


    