from .graphs import generateAllMotes24hRaw
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from .models import Device, Data, Graph, ExtendUser, New
import os
from dotenv import load_dotenv
import json

from .validation import validate

from django.contrib.auth import authenticate, login, logout

load_dotenv()

from .forms import DeviceForm

# Create your views here.

# Render

## General pages

def index(request):
    return render(request, 'home.html')


def dashboard(request):
    allWMotes24hRaw = Graph.objects.get(type=1)
    allEMotes24hRaw = Graph.objects.get(type=2)
    allGMotes24hRaw = Graph.objects.get(type=3)

    return render(request, 'dashboard.html', {'wMote': allWMotes24hRaw, 'eMote': allEMotes24hRaw, 'gMote': allGMotes24hRaw})

def members(request):
    advisors = ExtendUser.objects.all().filter(
        is_advisor=True).order_by('username')
    activeMembers = ExtendUser.objects.all().filter(
        is_active=True, is_advisor=False).order_by('username')
    oldMembers = ExtendUser.objects.all().filter(
        is_active=False, is_advisor=False).order_by('username')

    return render(request, 'members.html',
                  {'advisors': advisors, 'activeMembers': activeMembers, 'oldMembers': oldMembers})

def news(request):
    internNews = New.objects.select_related(
        'user').order_by('created_at').reverse()
    gitToken = os.getenv("GITTOKEN")

    return render(request, 'news.html', {'internNews': internNews, 'gitToken': gitToken})

## User pages functions

@login_required(login_url='/login')
@user_passes_test(lambda u: u.is_superuser, login_url='/login')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@user_passes_test(lambda u: u.is_superuser, login_url='/login')
def listMembersUpdate(request):
    if request.method == 'GET':
        membersUpdate = ExtendUser.objects.all()
        return render(request, 'listMembersUpdate.html', {'members': membersUpdate})

#  registration, authentication and logout user

@user_passes_test(lambda u: u.is_superuser, login_url='/login')
def register_user(request):
    if request.method == 'POST':
        errors = validate(request)
        if errors:
            return render(request, 'register.html', {'errors': errors})

        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        description = request.POST['description']
        profile_photo = request.FILES.get('profile_photo')
        is_advisor = False
        if request.POST.get('is_advisor') == 'on':
            is_advisor = True

        user = ExtendUser.objects.create_user(username=username,
                                              first_name=first_name,
                                              last_name=last_name,
                                              email=email,
                                              password=password,
                                              description=description,
                                              profile_photo=profile_photo,
                                              is_advisor=is_advisor
                                              )
        user.save()
        return render(request, 'register.html', {'user': user, 'message': 'user successfully registered'})

    return render(request, 'register.html')

@login_required(login_url='/login')
def update_user(request, id_user):
    user = request.user
    if not user.is_superuser:
        id_user = user.id

    user_update = get_object_or_404(ExtendUser, id=id_user)

    if request.method == 'POST':
        user_update.username = request.POST['username']
        user_update.first_name = request.POST['first_name']
        user_update.last_name = request.POST['last_name']
        user_update.email = request.POST['email']
        user_update.description = request.POST['description']
        user_update.is_advisor = 'is_advisor' in request.POST
        user_update.profile_photo = request.FILES.get('profile_photo')

        if request.POST.get('password'):
            user_update.set_password(request.POST['password'])

        user_update.save()
        return redirect('ListMembers')

    return render(request, 'register.html', {'user_update': user_update})

def login_user(request):
    # login
    user_auth = request.user

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        try:
            user_aux = ExtendUser.objects.get(email=email)
        except ExtendUser.DoesNotExist:
            return render(request, 'login.html', {'error': 'User not found'})

        user = authenticate(request, username=user_aux.username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_superuser:
                    return redirect('AdminDashboard')
                else:
                    return redirect('UpdateUser', id_user=user.id)

            else:
                return render(request, 'login.html', {'error': 'User account is inactive'})
        else:
            return render(request, 'login.html', {'error': 'User or password incorrect'})

    if user_auth.id is not None:
        if user_auth.is_superuser:
            return redirect('AdminDashboard')
        else:
            return redirect('UpdateUser', id_user=user_auth.id)

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('Login')

## Devices pages functions

def device_create(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'device_create.html', {'form': form})

def device_list(request):
    filter_type = request.GET.get('filter_type', '')
    filter_location = request.GET.get('filter_location', '')
    filter_section = request.GET.get('filter_section', '')
    filter_authorized = request.GET.get('filter_authorized', '')

    devices = Device.objects.all()

    if filter_type:
        devices = devices.filter(type=filter_type)
    if filter_location:
        devices = devices.filter(location=filter_location)
    if filter_section:
        devices = devices.filter(section=filter_section)
    if filter_authorized:
        devices = devices.filter(is_authorized=(filter_authorized == 'true'))

    locations = Device.objects.values_list('location', flat=True).distinct()
    sections = Device.objects.values_list('section', flat=True).distinct()

    context = {
        'devices': devices,
        'locations': locations,
        'sections': sections,
        'filter_type': filter_type,
        'filter_location': filter_location,
        'filter_section': filter_section,
        'filter_authorized': filter_authorized,
    }
    return render(request, 'device_list.html', context)

def edit_device(request, device_id):
    device = Device.objects.get(pk=device_id)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect('device_list')
    else:
        form = DeviceForm(instance=device)

    context = {'form': form, 'device': device}
    return render(request, 'edit_device.html', context)
        

def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    return render(request, 'device_detail.html', {'device': device})
  
# API

@api_view(['POST'])
def authenticateDevice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        macAddress = data['macAddress']
        deviceIp = data['deviceIp']
        

        if Device.objects.all().filter(mac_address=macAddress).exists():
            apiToken = uuid.uuid4()

            device = Device.objects.get(mac_address=macAddress)
            device.api_token = str(apiToken)
            device.save()

            return Response({'api_token': apiToken, 'deviceName': device.name}, status=status.HTTP_200_OK)
        else:
            apiToken = uuid.uuid4()

            try:
                newDevice = Device(mac_address=macAddress, ip_address=deviceIp, api_token=apiToken)
                newDevice.save()
            except:
                return Response({'error': 'something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'api_token': apiToken}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def storeData(request):
    if request.method == "POST":
        data = json.loads(request.body)
        apiToken = data["apiToken"]
        measure = data["measure"]
    

    # Device verification
    if not Device.objects.all().filter(api_token=apiToken).exists():
        return Response({'message': 'invalid api token.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not Device.objects.get(api_token=apiToken).is_authorized == 2:
        return Response({'message': 'device not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)

    if apiToken and measure is not None:
        for i in measure:
            device = Device.objects.get(api_token=apiToken)
            try:
                total = Data.objects.all().filter(device=device, type=i["type"]).order_by('id').reverse()
                
                if total:
                    storeData = Data(device=device, type=i["type"], last_collection=float(i["value"]), total=(float(total[0].total) + float(i["value"])))
                    storeData.save()
                else: 
                    storeData = Data(device=device, type=i["type"], last_collection=float(i["value"]), total=float(i["value"]))
                    storeData.save()
                
                return Response({'message': 'data stored.'}, status=status.HTTP_200_OK)
            except:
                return Response({'message': 'something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({'message': 'data not received.'}, status=status.HTTP_400_BAD_REQUEST)



## Exceptions
def page_in_erro403(request, exception):
    return render(request, 'error_403.html', status=403)


def page_in_erro404(request, exception):
    return render(request, 'error_404.html', status=404)


def page_in_erro500(request):
    return render(request, 'error_500.html', status=500)


def page_in_erro503(request):
    return render(request, 'error_503.html', status=503)
