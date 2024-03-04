from django.contrib import admin
from .models import Product

# Register your models here.
from dynfilters.filters import DynamicFilter
admin.site.register(Product)

# class PersonAdmin(admin.ModelAdmin):
#     ...
#     list_filter = (DynamicFilter,)

#     dynfilters_fields = [
#         '-',
#         'first_name',
#         'last_name',
#         ('first_name|last_name', 'Name'),   # Will generate: Q(first_name=<value>) | Q(last_name=<value>)
#         ('birth_date', 'Date of birth'),    # Requires the value to be: DD/MM/YYYY
#         '-',
#         ('address__town', 'City'),
#     ]

#     dynfilters_select_related = ['address'] # Optional
#     dynfilters_prefetch_related = []        # Optional