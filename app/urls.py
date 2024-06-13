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
    path('admin-dashboard', views.admin_dashboard, name='AdminDashboard'),
    path('members', views.members, name="Members"),
    path('news', views.news, name="News"),
    path('register', views.register_user, name='Register'),
    path('login', views.login_user, name='Login'),
    path('logout', views.logout_user, name='Logout'),
    path('listmembers', views.listMembersUpdate, name='ListMembers'),
    path('update/<int:id_user>/', views.update_user, name='UpdateUser')
]
