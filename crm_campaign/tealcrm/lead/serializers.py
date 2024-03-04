
from lead.models import Lead
from rest_framework import serializers

class LeadSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Lead
        fields = ('name', 'email', 'phone','description')
