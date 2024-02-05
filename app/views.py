from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid

from .models import Device

# Create your views here.


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

        print(deviceIp, deviceId)

    if Device.objects.all().filter(id=deviceId).exists():
        if Device.objects.get(id=deviceId).api_token == apiToken:
            if deviceId and deviceIp:
                deviceObject = Device.objects.get(id=deviceId)
                deviceObject.ip_address = str(deviceIp)
                deviceObject.save()

                return Response({'message': 'ip received.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'ip not received.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'api token does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'device does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)
