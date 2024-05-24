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
    path('api/get-device-ip', views.getDeviceIp, name='Receive IP'),
    path('api/identify-device', views.identifyDevice, name='Identify Device'),
    path('api/get-device-data', views.getDeviceData, name='Receive Data'),
    path('', views.index, name="Home"),
    path('dashboard', views.dashboard, name="Dashboard"),
    path('members', views.members, name="Members"),
    path('news', views.news, name="News"),
    path('device_create', views.device_create, name="Create Device"),
    path('device_list', views.device_list, name='device_list'),
    path('device_list/', views.device_list, name='device_list'),
    path('device_detail/<int:device_id>/', views.device_detail, name='device_detail'),
    path('edit/<int:device_id>/', views.edit_device, name='edit_device'),
    
]

