from .graphs import generateAllMotes24hRaw
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from .models import Device, Data, Graph, ExtendUser, New
import os
from dotenv import load_dotenv
load_dotenv()

from .forms import DeviceForm

# Create your views here.

# Render


def index(request):
    return render(request, 'home.html')


def dashboard(request):

    allWMotes24hRaw = Graph.objects.get(type=1)
    allEMotes24hRaw = Graph.objects.get(type=2)

    return render(request, 'dashboard.html', {'wMote': allWMotes24hRaw, 'eMote': allEMotes24hRaw})


def members(request):
    advisors = ExtendUser.objects.all().filter(
        is_advisor=True).order_by('username')
    activeMembers = ExtendUser.objects.all().filter(
        is_active=True, is_advisor=False).order_by('username')
    oldMembers = ExtendUser.objects.all().filter(
        is_active=False, is_advisor=False).order_by('username')

    return render(request, 'members.html', {'advisors': advisors, 'activeMembers': activeMembers, 'oldMembers': oldMembers})


def news(request):
    internNews = New.objects.select_related(
        'user').order_by('created_at').reverse()
    gitToken = os.getenv("GITTOKEN")

    return render(request, 'news.html', {'internNews': internNews, 'gitToken': gitToken})



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
def identifyDevice(request):
    if request.method == 'POST':
        macAddress = request.POST['macAddress']

        if Device.objects.all().filter(mac_address=macAddress).exists():
            apiToken = uuid.uuid4()

            device = Device.objects.get(mac_address=macAddress)
            device.api_token = str(apiToken)
            device.save()

            return Response({'id': device.id, 'api_token': apiToken}, status=status.HTTP_200_OK)
        else:
            id = uuid.uuid4()
            apiToken = uuid.uuid4()

            try:
                newDevice = Device(
                    id=id, mac_address=macAddress, api_token=apiToken)
                newDevice.save()
            except:
                return Response({'error': 'something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'id': id, 'api_token': apiToken}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def getDeviceIp(request):
    if request.method == "POST":
        deviceId = request.POST["deviceId"]
        deviceIp = request.POST["deviceIp"]
        apiToken = request.POST["apiToken"]

    if not Device.objects.all().filter(id=deviceId).exists():
        return Response({'message': 'device does not exist.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    if not Device.objects.get(id=deviceId).api_token == apiToken:
        return Response({'message': 'api token does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not Device.objects.get(id=deviceId).is_authorized == True:
        return Response({'message': 'device not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)

    if deviceId and deviceIp:
        deviceObject = Device.objects.get(id=deviceId)
        deviceObject.ip_address = str(deviceIp)
        deviceObject.save()

        return Response({'message': 'ip received.', 'deviceName': deviceObject.name}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'missing deviceId or deviceIp.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def getDeviceData(request):
    if request.method == "POST":
        deviceId = request.POST["deviceId"]
        apiToken = request.POST["apiToken"]
        volume = request.POST["volume"]

    if not Device.objects.all().filter(id=deviceId).exists():
        return Response({'message': 'device does not exist.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    if not Device.objects.get(id=deviceId).api_token == apiToken:
        return Response({'message': 'api token does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not Device.objects.get(id=deviceId).is_authorized == True:
        return Response({'message': 'device not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)

    if deviceId and volume:
        device = Device.objects.get(id=str(deviceId))
        total = Data.objects.all().filter(
            device=str(deviceId)).order_by('id').reverse()

        if (total):
            saveData = Data(device=device,
                            last_collection=float(volume), total=(float(total[0].total) + float(volume)))
            saveData.save()
        else:
            saveData = Data(device=device,
                            last_collection=float(volume), total=float(volume))
            saveData.save()

        return Response({'message': 'data received.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'data not received.'}, status=status.HTTP_400_BAD_REQUEST)

def page_in_erro403(request, exception):
    return render(request, 'error_403.html', status=403)

def page_in_erro404(request, exception):
    return render(request, 'error_404.html', status=404)

def page_in_erro500(request):
    return render(request, 'error_500.html', status=500)

def page_in_erro503(request):
    return render(request, 'error_503.html', status=503)