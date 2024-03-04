from django.urls import path

from. import views
from .form import SignupForm
app_name = 'userprofile'


urlpatterns = [
    path('myaccount',views.myaccount,name='myaccount' ),
    path('sign-up/',views.signup, name='signup'),
]