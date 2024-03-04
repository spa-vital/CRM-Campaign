"""
URL configuration for tealcrm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import index,about
from userprofile.views import signup
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from userprofile.form import LoginForm 

from django.conf import settings
from django.conf.urls.static import static




# Define your LoginView with a template_name attribute
class CustomLoginView(LoginView):
    template_name = 'userprofile/login.html'
class CustomLogoutView(LogoutView):
    template_name = ''

urlpatterns = [
    path('',index, name='index'),
    path('dashboard/clients/', include('client.urls')),
    path('dashboard/leads/', include('lead.urls')),
    path('dashboard/teams/',include('team.urls')),
    path('dashboard/', include('userprofile.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('about/',about, name='about'),
    path('log-in/', CustomLoginView.as_view(authentication_form =LoginForm), name='login'),
    path('log-out' ,CustomLogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),    
    path("__debug__/", include("debug_toolbar.urls")),
    path('dynfilters/', include('dynfilters.urls')),    
    path('campaign/', include('campaigns.urls')),
    path('templates/', include('templates.urls', namespace='templates')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


