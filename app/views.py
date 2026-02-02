from django.forms import ValidationError
from .graphs import generateAllMotes24hRaw
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from .models import Device, DeviceLog, Data, Graph, ExtendUser, New, DataTypes
import os
from dotenv import load_dotenv
import json
from datetime import timedelta, datetime
from django.http import JsonResponse

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
        return render(request, 'register.html', {'user': user, 'message': 'Usuário cadastrado com sucesso'})
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
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = []

        if password and confirm_password:
            if password != confirm_password:
                errors.append("As senhas não coincidem")
            else:
                user_update.set_password(password)

        if not errors:
            try:
                user_update.save()
                return redirect('ListMembers')
            except ValidationError as e:
                errors.extend(e.messages)

        return render(request, 'register.html', {'user_update': user_update, 'errors': errors})

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
            return render(request, 'login.html', {'error': 'Usuário não encontrado'})

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('UpdateUser', id_user=user.id)

            else:
                return render(request, 'login.html', {'error': 'A conta do usuário está inativa'})
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha incorretos'})

    if user_auth.id is not None:
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

def device_charts_page(request):
    devices = Device.objects.filter(is_authorized=2).order_by('name')
    return render(request, 'device_charts.html', {'devices': devices})

# API

@api_view(['POST'])
def authenticateDevice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        macAddress = data['macAddress']
        deviceIp = data['deviceIp']
        

        if Device.objects.all().filter(mac_address=macAddress, is_authorized=2).exists():
            apiToken = uuid.uuid4()
            device = Device.objects.get(mac_address=macAddress)
            device.api_token = str(apiToken)
            device.ip_address = str(deviceIp)
            deviceLog = DeviceLog(device=device, is_authorized=device.is_authorized, mac_address=device.mac_address, ip_address=device.ip_address, api_token=device.api_token)
            device.save()
            deviceLog.save()
            response_data = {
                'api_token': str(apiToken),
                'deviceName': device.name
            }
            if device.type == 2: 
                response_data['voltage'] = device.voltage if device.voltage else 127
            
            return Response(response_data, status=status.HTTP_200_OK)
        elif Device.objects.all().filter(mac_address=macAddress).exists():
            apiToken = uuid.uuid4()
            
            device = Device.objects.get(mac_address=macAddress)
            device.ip_address = str(deviceIp)
            device.api_token = apiToken
            
            deviceLog = DeviceLog(device=device, is_authorized=device.is_authorized, mac_address=device.mac_address, ip_address=device.ip_address, api_token=apiToken)
            
            device.save()
            deviceLog.save()
            
            return Response({'message': 'device not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                apiToken = uuid.uuid4()
                newDevice = Device(mac_address=macAddress, ip_address=deviceIp, api_token=apiToken)
                
                deviceLog = DeviceLog(device=newDevice, is_authorized=newDevice.is_authorized, mac_address=newDevice.mac_address, ip_address=newDevice.ip_address, api_token=apiToken)
            
                newDevice.save()
                deviceLog.save()
            except:
                return Response({'error': 'something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'device registered, await authorization'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def storeData(request):
    if request.method == "POST":
        data = json.loads(request.body)
        apiToken = data["apiToken"]
        macAddress = data['macAddress']
        measure = data["measure"]
    
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
                
            except:
                return Response({'message': 'something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'data stored.'}, status=status.HTTP_200_OK)

    else:
        return Response({'message': 'data not received.'}, status=status.HTTP_400_BAD_REQUEST)

def device_chart_data(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    if device.is_authorized != 2:
        return JsonResponse({'error': 'Dispositivo não autorizado'}, status=403)

    period = request.GET.get('period', '24h')

    now = datetime.now()
    if period == '24h':
        start_date = now - timedelta(hours=24)
    elif period == '7d':
        start_date = now - timedelta(days=7)
    elif period == '30d':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(hours=24)
    
    if device.type == 1:  
        data_types = [1] 
    elif device.type == 2: 
        data_types = [2, 4]  
    elif device.type == 3: 
        data_types = [3] 
    else:
        data_types = [1]  
    

    response_data = {
        'device_id': device.id,
        'device_name': device.name,
        'device_type': device.type,
        'period': period,
        'stats': {},
        'consumption_summary': {},
        'charts': {}
    }
    

    for data_type in data_types:
        try:
            data_type_name = DataTypes(data_type).label
            

            data_entries = Data.objects.filter(
                device=device,
                type=data_type,
                collect_date__gte=start_date
            ).order_by('collect_date')
            
            if not data_entries.exists():
                continue
            
            labels = []
            values = []
            total_consumption = 0
            
            for entry in data_entries:
                local_time = entry.collect_date - timedelta(hours=3)
                
                if period == '24h':
                    label = local_time.strftime('%H:%M')
                elif period == '7d':
                    label = local_time.strftime('%d/%m %Hh')
                else:  
                    label = local_time.strftime('%d/%m')
                
                labels.append(label)
                values.append(float(entry.last_collection))
                total_consumption += float(entry.last_collection)
            
            if values:
                current_value = values[-1]
                max_value = max(values)
                min_value = min(values)
                avg_value = sum(values) / len(values)
                

                trend = 0
                if len(values) > 1:
                    previous_value = values[-2] if len(values) >= 2 else values[0]
                    if previous_value > 0:
                        trend = ((current_value - previous_value) / previous_value) * 100
                
                response_data['stats'][data_type_name] = {
                    'current': round(current_value, 3),
                    'max': round(max_value, 3),
                    'min': round(min_value, 3),
                    'average': round(avg_value, 3),
                    'trend': round(trend, 1)
                }
                
                response_data['consumption_summary'][data_type_name] = {
                    'total': round(total_consumption, 3),
                    'average': round(avg_value, 3),
                    'count': len(values)
                }
                
                if data_type in [1, 3]: 
                    if data_type == 1:  
                        kwh_equivalent = total_consumption * 0.3 / 1000 
                    elif data_type == 3: 
                        kwh_equivalent = total_consumption * 10.55 / 1000 
                    
                    response_data['consumption_summary'][data_type_name]['kwh_equivalent'] = round(kwh_equivalent, 2)
                
                if len(values) > 100:
                    step = len(values) // 50
                    sampled_labels = labels[::step]
                    sampled_values = values[::step]
                else:
                    sampled_labels = labels
                    sampled_values = values
                
                response_data['charts'][data_type_name] = {
                    'labels': sampled_labels,
                    'values': sampled_values,
                    'count': len(sampled_values)
                }
                
        except Exception as e:
            print(f"Erro processando tipo {data_type}: {str(e)}")
            continue
    
    return JsonResponse(response_data)

# Error pages

def page_in_erro403(request, exception):
    return render(request, 'error_403.html', status=403)


def page_in_erro404(request, exception):
    return render(request, 'error_404.html', status=404)


def page_in_erro500(request):
    return render(request, 'error_500.html', status=500)


def page_in_erro503(request):
    return render(request, 'error_503.html', status=503)