from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from lead.models import Lead
from client.models import Client
from team.models import Team
from django.db.models import Count
from campaigns.models import Campaign
from dynfilters.models import DynamicFilterExpr
from django.template.loader import render_to_string
import json
@login_required
def dashboard(request):
    team = request.user.userprofile.active_team

    leads = Lead.objects.filter(team=team, converted_to_client = False).order_by('-created_at') [0:5]
    clients = Client.objects.filter(team=team).order_by('-created_at') [0:5]
    leads_count = Lead.objects.filter(converted_to_client = False).count()  # Lấy tất cả các lead
    
    clients_count = Client.objects.count()  # Lấy tất cả các client
    leads_by_status = Lead.objects.values('status').annotate(count=Count('status'))

    lead_convert = Lead.objects.filter(team=team, converted_to_client=True).order_by('-created_at') [0:5]

    leads_convert_count =  Lead.objects.filter(converted_to_client=True).count()
    lead_sources_website = Lead.objects.filter(lead_source=1).count()
    lead_sources_social = Lead.objects.filter(lead_source=2).count()
    lead_sources_referrals = Lead.objects.filter(lead_source=3).count()
    lead_sources_ads = Lead.objects.filter(lead_source=4).count()



    # Sử dụng annotate và Count để đếm số lượng chiến dịch cho mỗi filter
    data = (
        DynamicFilterExpr.objects
        .annotate(num_campaigns=Count('campaigns'))
        .values_list('name', 'num_campaigns')
    )
    labels, data = zip(*data)
    chart_data = {
        'labels': labels,
        'data': data,
    }
    
    # Chuyển đổi chart_data thành JSON
    chart_data_json = json.dumps(chart_data)

        

    # Dữ liệu cho biểu đồ
    lead_statuses = [lead['status'] for lead in leads_by_status]
    lead_counts = [lead['count'] for lead in leads_by_status]

    return render(request, 'dashboard/dashboard.html',{
        'leads':leads,
        'clients':clients,
        'leads_count': leads_count, 
        'clients_count': clients_count,
        'lead_statuses': lead_statuses,
        'lead_counts': lead_counts,
        'lead_convert': lead_convert,
        'leads_convert_count': leads_convert_count,
        'lead_sources_website': lead_sources_website,
        'lead_sources_social': lead_sources_social,
        'lead_sources_referrals': lead_sources_referrals,
        'lead_sources_ads': lead_sources_ads,
        'chart_data_json': chart_data_json,
    })



