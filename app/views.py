from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from .models import Device, Data, Graph, ExtendUser

# Create your views here.

# Render
from .graphs import generateAllMotes24hRaw


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
    return render(request, 'news.html')

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

    if Device.objects.all().filter(id=deviceId).exists():
        if Device.objects.get(id=deviceId).api_token == apiToken:
            if deviceId and deviceIp:
                deviceObject = Device.objects.get(id=deviceId)
                deviceObject.ip_address = str(deviceIp)
                deviceObject.save()

                print(deviceObject.name)

                return Response({'message': 'ip received.', 'deviceName': deviceObject.name}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'ip not received.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'api token does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'device does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def getDeviceData(request):
    if request.method == "POST":
        deviceId = request.POST["deviceId"]
        apiToken = request.POST["apiToken"]
        volume = request.POST["volume"]

    if Device.objects.all().filter(id=deviceId).exists():
        if Device.objects.get(id=deviceId).api_token == apiToken:
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
        else:
            return Response({'message': 'api token does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'message': 'device does not exist.'}, status=status.HTTP_404_NOT_FOUND)
