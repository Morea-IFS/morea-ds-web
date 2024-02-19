from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid

# Graphs
import plotly.express as px

from .models import Device, Data

# Create your views here.

# Render


def index(request):
    return render(request, 'home.html')


def dashboard(request):
    config = {'staticPlot': True}

    fig = px.line(x=["a", "b", "c"], y=[1, 3, 2], )
    fig.update_layout()
    fig.write_html('static/graphs/first_figure.html', config, )

    return render(request, 'dashboard.html')


def members(request):
    return render(request, 'members.html')


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
