"""morea_ds URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    ## General
    path('', views.index, name="Home"),
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
    
    ## Charts routes
    path('dashboard', views.device_charts_page, name='Dashboard'),
    path('api/device-chart-data/<int:device_id>/', views.device_chart_data, name='device_chart_data'),
    path('device-fullscreen/<int:device_id>/', views.device_fullscreen, name='device_fullscreen'),
]