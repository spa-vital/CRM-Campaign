from django.contrib import admin
from .models import Lead, Comment, LeadFile, LeadSource
# Register your models here.
from dynfilters.filters import DynamicFilter


@admin.register(Lead)
class Leaddmin(admin.ModelAdmin):
    list_filter = (DynamicFilter,)

    dynfilters_fields = [
        '-',
        'status',
        'last_name',
        'name',
        '-',
        ('lead_source__name','LeadSource'),
        ('product_line__name','Product'),
    ]

    dynfilters_select_related = ['product_line','lead_source'] # Optional
    dynfilters_prefetch_related = []    

admin.site.register(Comment)
admin.site.register(LeadFile)
admin.site.register(LeadSource)