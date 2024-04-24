from .graphs import generateAllMotes24hRaw
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from .models import Device, Data, Graph, ExtendUser, New
import os
from dotenv import load_dotenv
load_dotenv()

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
