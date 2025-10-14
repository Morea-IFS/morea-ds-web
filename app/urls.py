"""morea_ds URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    ## General
    path('', views.index, name="Home"),
    # path('dashboard', views.dashboard, name="Dashboard"),
    path('admin-dashboard', views.admin_dashboard, name='AdminDashboard'),
    path('members', views.members, name="Members"),
    path('news', views.news, name="News"),
    ## API related
    path('api/authenticate', views.authenticateDevice, name='Authenticate Device'),
    path('api/store-data', views.storeData, name='Receive Data'),
    ## Devices related
    path('device-create', views.device_create, name="Create Device"),
    path('device-list', views.device_list, name='device_list'),
    path('device-list/', views.device_list, name='device_list'),
    path('device-detail/<int:device_id>/', views.device_detail, name='device_detail'),
    path('edit/<int:device_id>/', views.edit_device, name='edit_device'),
    ## Members related
    path('register', views.register_user, name='Register'),
    path('login', views.login_user, name='Login'),
    path('logout', views.logout_user, name='Logout'),
    path('list-members', views.listMembersUpdate, name='ListMembers'),
    path('update/<int:id_user>/', views.update_user, name='UpdateUser'),
    ## New charts routes
    path('dashboard', views.device_charts_page, name='Dashboard'),
    path('api/device-chart-data/<int:device_id>/', views.device_chart_data, name='device_chart_data'),
]